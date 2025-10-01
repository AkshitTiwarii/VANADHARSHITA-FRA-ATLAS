// Service Worker for PWA offline functionality
const CACHE_NAME = 'fra-portal-v1.0.0';
const OFFLINE_URL = '/offline.html';

// Resources to cache for offline use
const urlsToCache = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/offline.html',
  // Core pages
  '/dashboard', 
  '/citizen-portal',
  '/atlas',
  // Translation files
  '/translations/en.json',
  '/translations/hi.json',
  '/translations/bn.json',
  '/translations/or.json',
  '/translations/te.json',
  // Images and icons
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png'
];

// API endpoints to cache
const apiCache = [
  '/api/villages',
  '/api/claims',
  '/api/districts',
  '/api/states'
];

// Install Service Worker
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[ServiceWorker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        // Skip waiting to activate immediately
        return self.skipWaiting();
      })
  );
});

// Activate Service Worker
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      // Claim clients to ensure immediate control
      return self.clients.claim();
    })
  );
});

// Fetch Strategy: Network First for API, Cache First for static resources
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests with Network First strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      networkFirstStrategy(request)
    );
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(
      networkFirstStrategy(request)
        .catch(() => {
          return caches.match(OFFLINE_URL);
        })
    );
    return;
  }

  // Handle static resources with Cache First strategy
  event.respondWith(
    cacheFirstStrategy(request)
  );
});

// Network First Strategy (for API and dynamic content)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    
    // Cache successful API responses
    if (networkResponse.ok && request.url.includes('/api/')) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[ServiceWorker] Network failed, trying cache');
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline response for failed API calls
    if (request.url.includes('/api/')) {
      return new Response(
        JSON.stringify({
          error: 'Offline - Data not available',
          offline: true,
          cached: false
        }),
        {
          status: 503,
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    throw error;
  }
}

// Cache First Strategy (for static resources)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[ServiceWorker] Failed to fetch resource:', request.url);
    throw error;
  }
}

// Background Sync for offline form submissions
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync', event.tag);
  
  if (event.tag === 'claim-submission') {
    event.waitUntil(syncClaimSubmissions());
  }
  
  if (event.tag === 'document-upload') {
    event.waitUntil(syncDocumentUploads());
  }
});

// Sync offline claim submissions when back online
async function syncClaimSubmissions() {
  try {
    const db = await openIndexedDB();
    const pendingClaims = await getStoredData(db, 'pendingClaims');
    
    for (const claim of pendingClaims) {
      try {
        const response = await fetch('/api/claims', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': claim.authToken
          },
          body: JSON.stringify(claim.data)
        });
        
        if (response.ok) {
          await removeStoredData(db, 'pendingClaims', claim.id);
          console.log('[ServiceWorker] Synced claim:', claim.id);
        }
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync claim:', claim.id, error);
      }
    }
  } catch (error) {
    console.error('[ServiceWorker] Sync failed:', error);
  }
}

// Sync offline document uploads when back online
async function syncDocumentUploads() {
  try {
    const db = await openIndexedDB();
    const pendingUploads = await getStoredData(db, 'pendingUploads');
    
    for (const upload of pendingUploads) {
      try {
        const formData = new FormData();
        formData.append('file', upload.file);
        formData.append('claimId', upload.claimId);
        formData.append('documentType', upload.documentType);
        
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          headers: {
            'Authorization': upload.authToken
          },
          body: formData
        });
        
        if (response.ok) {
          await removeStoredData(db, 'pendingUploads', upload.id);
          console.log('[ServiceWorker] Synced upload:', upload.id);
        }
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync upload:', upload.id, error);
      }
    }
  } catch (error) {
    console.error('[ServiceWorker] Upload sync failed:', error);
  }
}

// IndexedDB helpers for offline data storage
function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('FRAPortalDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      if (!db.objectStoreNames.contains('pendingClaims')) {
        db.createObjectStore('pendingClaims', { keyPath: 'id' });
      }
      
      if (!db.objectStoreNames.contains('pendingUploads')) {
        db.createObjectStore('pendingUploads', { keyPath: 'id' });
      }
      
      if (!db.objectStoreNames.contains('cachedData')) {
        db.createObjectStore('cachedData', { keyPath: 'key' });
      }
    };
  });
}

function getStoredData(db, storeName) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly');
    const store = transaction.objectStore(storeName);
    const request = store.getAll();
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
  });
}

function removeStoredData(db, storeName, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite');
    const store = transaction.objectStore(storeName);
    const request = store.delete(id);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve();
  });
}

// Push Notifications for claim status updates
self.addEventListener('push', (event) => {
  console.log('[ServiceWorker] Push received');
  
  const options = {
    body: 'You have updates on your forest rights claim',
    icon: '/logo192.png',
    badge: '/icons/badge-96x96.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details',
        icon: '/icons/view-96x96.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/close-96x96.png'
      }
    ]
  };
  
  if (event.data) {
    const payload = event.data.json();
    options.body = payload.message || options.body;
    options.data = { ...options.data, ...payload };
  }
  
  event.waitUntil(
    self.registration.showNotification('FRA Portal', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[ServiceWorker] Notification click received');
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/citizen-portal')
    );
  } else if (event.action === 'close') {
    // Just close the notification
    return;
  } else {
    // Default action - open the app
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Share Target API support
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  if (url.pathname === '/share-target/' && event.request.method === 'POST') {
    event.respondWith(handleSharedContent(event.request));
  }
});

async function handleSharedContent(request) {
  const formData = await request.formData();
  const title = formData.get('title') || '';
  const text = formData.get('text') || '';
  const url = formData.get('url') || '';
  const files = formData.getAll('documents');
  
  // Store shared content for processing when app opens
  const db = await openIndexedDB();
  const transaction = db.transaction(['cachedData'], 'readwrite');
  const store = transaction.objectStore('cachedData');
  
  await store.put({
    key: 'sharedContent',
    data: { title, text, url, files: files.length },
    timestamp: Date.now()
  });
  
  // Redirect to claim filing page
  return Response.redirect('/citizen-portal?shared=true', 302);
}