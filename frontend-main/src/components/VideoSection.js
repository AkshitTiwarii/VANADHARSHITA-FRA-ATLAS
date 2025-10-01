import React, { useState } from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { Play, Upload, X } from 'lucide-react';

const VideoSection = ({ 
  videoUrl = null, 
  onVideoUpload = null, 
  showUploadButton = false,
  title = "Project Overview Video",
  description = "Watch how our platform is revolutionizing forest rights management across India"
}) => {
  const { t } = useTranslation();
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file && onVideoUpload) {
      // Create a URL for the uploaded file
      const videoURL = URL.createObjectURL(file);
      onVideoUpload(videoURL);
    }
  };

  const VideoPlayer = ({ src, onClose }) => (
    <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4">
      <div className="relative max-w-6xl max-h-full">
        <button
          onClick={onClose}
          className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors"
        >
          <X className="w-8 h-8" />
        </button>
        <video
          src={src}
          controls
          autoPlay
          className="w-full h-auto max-h-[80vh] rounded-lg shadow-2xl"
        >
          Your browser does not support the video tag.
        </video>
      </div>
    </div>
  );

  return (
    <div className="mb-16">
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-2xl p-8 shadow-2xl">
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-white mb-3">
            {title}
          </h3>
          <p className="text-gray-300">
            {description}
          </p>
        </div>
        
        <div className="relative bg-black rounded-xl overflow-hidden shadow-2xl aspect-video">
          {videoUrl ? (
            // Video is available
            <div className="relative group cursor-pointer" onClick={() => setIsVideoModalOpen(true)}>
              <video
                src={videoUrl}
                className="w-full h-full object-cover"
                poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 675'%3E%3Cdefs%3E%3ClinearGradient id='bg' x1='0%25' y1='0%25' x2='100%25' y2='100%25'%3E%3Cstop offset='0%25' style='stop-color:%23065f46;stop-opacity:1' /%3E%3Cstop offset='100%25' style='stop-color:%231e40af;stop-opacity:1' /%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='1200' height='675' fill='url(%23bg)'/%3E%3C/svg%3E"
              />
              <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-all duration-300 flex items-center justify-center">
                <div className="w-20 h-20 bg-white/90 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-2xl">
                  <Play className="w-8 h-8 text-gray-900 ml-1" fill="currentColor" />
                </div>
              </div>
            </div>
          ) : (
            // Video placeholder
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-green-900/50 to-blue-900/50">
              <div className="text-center text-white">
                <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 backdrop-blur-sm">
                  <div className="w-0 h-0 border-l-[12px] border-l-white border-y-[8px] border-y-transparent ml-1"></div>
                </div>
                <p className="text-lg font-semibold">{t('videoComingSoon')}</p>
                <p className="text-sm text-gray-300 mt-2">{t('videoComingSoonDesc')}</p>
                
                {showUploadButton && (
                  <div className="mt-6">
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleVideoUpload}
                      className="hidden"
                      id="video-upload"
                    />
                    <label
                      htmlFor="video-upload"
                      className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold cursor-pointer transition-colors"
                    >
                      <Upload className="w-5 h-5" />
                      Upload Video
                    </label>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Video Modal */}
      {isVideoModalOpen && videoUrl && (
        <VideoPlayer 
          src={videoUrl} 
          onClose={() => setIsVideoModalOpen(false)} 
        />
      )}
    </div>
  );
};

export default VideoSection;