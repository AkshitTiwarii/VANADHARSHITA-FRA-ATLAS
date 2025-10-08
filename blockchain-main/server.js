const express = require('express');
const cors = require('cors');
const crypto = require('crypto');

// Simple in-memory blockchain
class SimpleBlockchain {
  constructor() {
    this.blocks = [];
    this.pendingTransactions = [];
    this.createGenesisBlock();
  }

  createGenesisBlock() {
    const genesisBlock = {
      index: 0,
      timestamp: new Date().toISOString(),
      transactions: [],
      previousHash: '0',
      hash: this.calculateHash(0, new Date().toISOString(), [], '0')
    };
    this.blocks.push(genesisBlock);
  }

  calculateHash(index, timestamp, transactions, previousHash) {
    const data = index + timestamp + JSON.stringify(transactions) + previousHash;
    return crypto.createHash('sha256').update(data).digest('hex');
  }

  getLatestBlock() {
    return this.blocks[this.blocks.length - 1];
  }

  addTransaction(transaction) {
    this.pendingTransactions.push(transaction);
  }

  minePendingTransactions() {
    const block = {
      index: this.blocks.length,
      timestamp: new Date().toISOString(),
      transactions: this.pendingTransactions,
      previousHash: this.getLatestBlock().hash
    };
    
    block.hash = this.calculateHash(block.index, block.timestamp, block.transactions, block.previousHash);
    this.blocks.push(block);
    this.pendingTransactions = [];
    return block;
  }

  getTransaction(transactionId) {
    for (let block of this.blocks) {
      for (let transaction of block.transactions) {
        if (transaction.id === transactionId) {
          return { transaction, block };
        }
      }
    }
    return null;
  }
}

// Initialize blockchain
const blockchain = new SimpleBlockchain();

// Initialize Express app
const app = express();
const PORT = 8001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Helper functions
function generateDocumentHash(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function generateMetadataHash(metadata) {
  return crypto.createHash('sha256').update(JSON.stringify(metadata || {})).digest('hex');
}

function generateTransactionId() {
  return crypto.randomBytes(16).toString('hex');
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'blockchain-verification',
    version: '1.0.0',
    blocks: blockchain.blocks.length,
    pendingTransactions: blockchain.pendingTransactions.length
  });
});

// Submit document verification to blockchain
app.post('/api/submit-verification', async (req, res) => {
  try {
    const { documentHash, metadata, ocrText, coordinates } = req.body;
    
    if (!documentHash) {
      return res.status(400).json({
        success: false,
        error: 'Document hash is required'
      });
    }

    // Generate transaction
    const transactionId = generateTransactionId();
    const metadataHash = generateMetadataHash(metadata);
    const combinedHash = crypto.createHash('sha256')
      .update(documentHash + metadataHash)
      .digest('hex');

    const transaction = {
      id: transactionId,
      type: 'DOCUMENT_VERIFICATION',
      documentHash,
      metadataHash,
      combinedHash,
      timestamp: new Date().toISOString(),
      metadata: metadata || {},
      ocrText: ocrText || '',
      coordinates: coordinates || {},
      status: 'VERIFIED'
    };

    // Add to blockchain
    blockchain.addTransaction(transaction);
    const block = blockchain.minePendingTransactions();

    console.log(`New verification transaction: ${transactionId}`);
    console.log(`Added to block: ${block.index}`);

    res.json({
      success: true,
      transactionId,
      blockNumber: block.index,
      documentHash,
      metadataHash,
      combinedHash,
      timestamp: transaction.timestamp,
      blockHash: block.hash
    });

  } catch (error) {
    console.error('Blockchain verification error:', error);
    res.status(500).json({
      success: false,
      error: 'Blockchain verification failed'
    });
  }
});

// Get verification status
app.get('/api/verification/:transactionId', (req, res) => {
  try {
    const { transactionId } = req.params;
    const result = blockchain.getTransaction(transactionId);
    
    if (!result) {
      return res.status(404).json({
        success: false,
        error: 'Transaction not found'
      });
    }

    res.json({
      success: true,
      transaction: result.transaction,
      block: {
        index: result.block.index,
        hash: result.block.hash,
        timestamp: result.block.timestamp
      }
    });

  } catch (error) {
    console.error('Verification lookup error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to lookup verification'
    });
  }
});

// Get blockchain status
app.get('/api/blockchain/status', (req, res) => {
  res.json({
    success: true,
    blockchain: {
      totalBlocks: blockchain.blocks.length,
      pendingTransactions: blockchain.pendingTransactions.length,
      latestBlock: blockchain.getLatestBlock(),
      genesisBlock: blockchain.blocks[0]
    }
  });
});

// ===== FRA CLAIM ANTI-FRAUD ENDPOINTS =====

// Helper: Check for duplicate claims
function checkDuplicateClaim(aadhaarHash, gps, areaHectares) {
  for (let block of blockchain.blocks) {
    for (let transaction of block.transactions) {
      if (transaction.type === 'FRA_CLAIM') {
        // Check same person
        if (transaction.aadhaar_hash === aadhaarHash) {
          // Check GPS overlap (simple distance check)
          const existingGPS = transaction.gps.split(',').map(x => parseFloat(x.trim()));
          const newGPS = gps.split(',').map(x => parseFloat(x.trim()));
          
          const latDiff = Math.abs(existingGPS[0] - newGPS[0]);
          const lngDiff = Math.abs(existingGPS[1] - newGPS[1]);
          
          // If within 0.01 degrees (~1km), consider it overlap
          if (latDiff < 0.01 && lngDiff < 0.01) {
            return {
              isDuplicate: true,
              reason: 'Same claimant has existing claim on overlapping land',
              existingClaimId: transaction.claimId,
              existingStatus: transaction.status,
              overlap: Math.round((1 - Math.max(latDiff, lngDiff) / 0.01) * 100)
            };
          }
        }
      }
    }
  }
  return { isDuplicate: false };
}

// Helper: Check for duplicate scheme
function checkDuplicateScheme(claimId, schemeId) {
  for (let block of blockchain.blocks) {
    for (let transaction of block.transactions) {
      if (transaction.type === 'SCHEME_APPLICATION' && 
          transaction.claimId === claimId && 
          transaction.schemeId === schemeId) {
        return {
          isDuplicate: true,
          reason: 'Scheme already claimed',
          claimed_date: transaction.timestamp,
          benefits_received: transaction.benefitAmount
        };
      }
    }
  }
  return { isDuplicate: false };
}

// Submit FRA claim
app.post('/api/blockchain/submit-claim', async (req, res) => {
  try {
    const { claimId, claimant_name, aadhaar_hash, gps, area_hectares, claim_type } = req.body;
    
    if (!claimId || !aadhaar_hash || !gps) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: claimId, aadhaar_hash, gps'
      });
    }

    // Check for duplicates
    const duplicateCheck = checkDuplicateClaim(aadhaar_hash, gps, area_hectares);
    
    if (duplicateCheck.isDuplicate) {
      console.log(`❌ Duplicate claim detected: ${claimId}`);
      return res.status(409).json({
        success: false,
        isDuplicate: true,
        reason: duplicateCheck.reason,
        existingClaimId: duplicateCheck.existingClaimId,
        existingStatus: duplicateCheck.existingStatus,
        overlap: duplicateCheck.overlap
      });
    }

    // Create transaction
    const transactionId = generateTransactionId();
    const transaction = {
      id: transactionId,
      type: 'FRA_CLAIM',
      claimId,
      claimant_name,
      aadhaar_hash,
      gps,
      area_hectares,
      claim_type,
      timestamp: new Date().toISOString(),
      status: 'submitted',
      schemes: []
    };

    blockchain.addTransaction(transaction);
    const block = blockchain.minePendingTransactions();

    console.log(`✅ New FRA claim: ${claimId} (Block ${block.index})`);

    res.json({
      success: true,
      claimId,
      transactionId,
      blockNumber: block.index,
      blockHash: block.hash,
      timestamp: transaction.timestamp,
      status: 'submitted'
    });

  } catch (error) {
    console.error('Claim submission error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to submit claim'
    });
  }
});

// Apply for scheme
app.post('/api/blockchain/apply-scheme', async (req, res) => {
  try {
    const { claimId, schemeId, schemeName, benefitAmount } = req.body;
    
    if (!claimId || !schemeId) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: claimId, schemeId'
      });
    }

    // Check for duplicate scheme application
    const duplicateCheck = checkDuplicateScheme(claimId, schemeId);
    
    if (duplicateCheck.isDuplicate) {
      console.log(`❌ Duplicate scheme detected: ${schemeId} for ${claimId}`);
      return res.status(409).json({
        success: false,
        isDuplicate: true,
        reason: duplicateCheck.reason,
        claimed_date: duplicateCheck.claimed_date,
        benefits_received: duplicateCheck.benefits_received
      });
    }

    // Create transaction
    const transactionId = generateTransactionId();
    const transaction = {
      id: transactionId,
      type: 'SCHEME_APPLICATION',
      claimId,
      schemeId,
      schemeName,
      benefitAmount,
      timestamp: new Date().toISOString(),
      status: 'approved'
    };

    blockchain.addTransaction(transaction);
    const block = blockchain.minePendingTransactions();

    console.log(`✅ Scheme approved: ${schemeId} for ${claimId} (Block ${block.index})`);

    res.json({
      success: true,
      claimId,
      schemeId,
      transactionId,
      blockNumber: block.index,
      blockHash: block.hash,
      timestamp: transaction.timestamp,
      status: 'approved'
    });

  } catch (error) {
    console.error('Scheme application error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to apply for scheme'
    });
  }
});

// Check for duplicate claim (query endpoint)
app.post('/api/blockchain/check-duplicate', async (req, res) => {
  try {
    const { aadhaar_hash, gps, area_hectares } = req.body;
    
    const result = checkDuplicateClaim(aadhaar_hash, gps, area_hectares);
    
    res.json({
      isDuplicate: result.isDuplicate,
      ...(result.isDuplicate && {
        existingClaim: {
          claimId: result.existingClaimId,
          status: result.existingStatus,
          overlap: result.overlap
        },
        recommendation: 'REJECT - Duplicate claim'
      })
    });

  } catch (error) {
    console.error('Duplicate check error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to check duplicate'
    });
  }
});

// Check scheme eligibility
app.post('/api/blockchain/check-scheme', async (req, res) => {
  try {
    const { claimId, schemeId } = req.body;
    
    const result = checkDuplicateScheme(claimId, schemeId);
    
    res.json({
      alreadyClaimed: result.isDuplicate,
      ...(result.isDuplicate && {
        schemeDetails: {
          name: schemeId,
          claimed_date: result.claimed_date,
          benefit_amount: result.benefits_received
        },
        recommendation: 'REJECT - Already receiving benefits'
      })
    });

  } catch (error) {
    console.error('Scheme check error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to check scheme'
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🔗 Blockchain Service running on port ${PORT}`);
  console.log(`🔍 Health check: http://localhost:${PORT}/health`);
  console.log(`📊 Blockchain status: http://localhost:${PORT}/api/blockchain/status`);
  console.log(`🛡️  Anti-fraud endpoints: /api/blockchain/submit-claim, /api/blockchain/apply-scheme`);
});