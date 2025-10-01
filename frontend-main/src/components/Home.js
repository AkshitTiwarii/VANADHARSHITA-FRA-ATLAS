import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../contexts/LanguageContext';
import LanguageSelector from './LanguageSelector';
import { useAuth } from '../App';
import { 
  TreePine, 
  Users, 
  FileText, 
  BarChart3, 
  Shield,
  MapPin,
  ArrowRight,
  Globe,
  Award,
  User,
  LogOut,
  Scale,
  BookOpen,
  CheckCircle,
  AlertTriangle,
  Zap,
  Database,
  Eye,
  Smartphone,
  Brain,
  Lock,
  Clock,
  Target
} from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { user, logout } = useAuth();

  const features = [
    {
      icon: <FileText className="w-8 h-8 text-green-600" />,
      title: t('caseManagement'),
      description: t('caseManagementDesc'),
      path: '/cases',
      color: 'bg-green-50 hover:bg-green-100'
    },
    {
      icon: <TreePine className="w-8 h-8 text-blue-600" />,
      title: t('forestAtlas'),
      description: t('forestAtlasDesc'),
      path: '/atlas',
      color: 'bg-blue-50 hover:bg-blue-100'
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-purple-600" />,
      title: t('analytics'),
      description: t('analyticsDesc'),
      path: '/analytics',
      color: 'bg-purple-50 hover:bg-purple-100'
    },
    {
      icon: <Shield className="w-8 h-8 text-orange-600" />,
      title: t('adminPanel'),
      description: t('adminPanelDesc'),
      path: '/admin',
      color: 'bg-orange-50 hover:bg-orange-100'
    }
  ];

  const stats = [
    {
      icon: <Users className="w-6 h-6 text-green-600" />,
      label: t('totalVillages'),
      value: '2,847',
      description: t('coveredUnderFRA')
    },
    {
      icon: <FileText className="w-6 h-6 text-blue-600" />,
      label: t('forestClaims'),
      value: '1,190',
      description: t('ifrCfrApplications')
    },
    {
      icon: <Award className="w-6 h-6 text-purple-600" />,
      label: t('approvedClaims'),
      value: '892',
      description: t('successfullyProcessed')
    },
    {
      icon: <Globe className="w-6 h-6 text-orange-600" />,
      label: t('schemesIntegrated'),
      value: '4',
      description: t('connectedToGovernment')
    }
  ];

  const problems = [
    {
      icon: <AlertTriangle className="w-6 h-6 text-red-600" />,
      title: t('historicalInjustice'),
      description: t('historicalInjusticeDesc')
    },
    {
      icon: <FileText className="w-6 h-6 text-orange-600" />,
      title: t('complexPaperwork'),
      description: t('complexPaperworkDesc')
    },
    {
      icon: <Clock className="w-6 h-6 text-blue-600" />,
      title: t('delayedProcessing'),
      description: t('delayedProcessingDesc')
    },
    {
      icon: <Eye className="w-6 h-6 text-purple-600" />,
      title: t('lackTransparency'),
      description: t('lackTransparencyDesc')
    }
  ];

  const solutions = [
    {
      icon: <Brain className="w-6 h-6 text-green-600" />,
      title: t('aiPoweredProcessing'),
      description: t('aiPoweredProcessingDesc')
    },
    {
      icon: <Smartphone className="w-6 h-6 text-blue-600" />,
      title: t('digitalAccessibility'),
      description: t('digitalAccessibilityDesc')
    },
    {
      icon: <Database className="w-6 h-6 text-purple-600" />,
      title: t('blockchainSecurity'),
      description: t('blockchainSecurityDesc')
    },
    {
      icon: <Globe className="w-6 h-6 text-orange-600" />,
      title: t('multilingualSupport'),
      description: t('multilingualSupportDesc')
    }
  ];

  const uniqueFeatures = [
    {
      icon: <Zap className="w-8 h-8 text-yellow-600" />,
      title: t('realTimeProcessing'),
      description: t('realTimeProcessingDesc'),
      highlight: t('minutes')
    },
    {
      icon: <Lock className="w-8 h-8 text-green-600" />,
      title: t('blockchainVerification'),
      description: t('blockchainVerificationDesc'),
      highlight: t('tamperProof')
    },
    {
      icon: <Target className="w-8 h-8 text-blue-600" />,
      title: t('satelliteMonitoring'),
      description: t('satelliteMonitoringDesc'),
      highlight: t('realTimeSatellite')
    },
    {
      icon: <Users className="w-8 h-8 text-purple-600" />,
      title: t('tribalLanguages'),
      description: t('tribalLanguagesDesc'),
      highlight: '9+ ' + t('languages')
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-teal-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-700 to-blue-700 bg-clip-text text-transparent">
                  {t('websiteName')}
                </h1>
                <p className="text-sm text-gray-600 font-medium">{t('websiteTagline')}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <LanguageSelector />
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <User className="w-4 h-4" />
                <span>{user?.username}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-1 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                {t('logout')}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 to-black/40"></div>
        <div 
          className="relative min-h-[70vh] flex items-center justify-center bg-cover bg-center"
          style={{
            backgroundImage: `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.3)), url('https://wallpapercave.com/wp/3ruMITV.jpg')`
          }}
        >
          <div className="text-center text-white px-6 max-w-5xl mx-auto">
            <div className="mb-8">
              <div className="inline-block px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6">
                <span className="text-green-200 font-semibold text-lg">{t('forestRightsRevolution')}</span>
              </div>
            </div>
            <h1 className="text-6xl md:text-8xl font-extrabold mb-8 leading-tight">
              <span className="bg-gradient-to-r from-green-300 via-blue-300 to-teal-300 bg-clip-text text-transparent drop-shadow-2xl">
                {t('websiteName')}
              </span>
            </h1>
            <h2 className="text-2xl md:text-4xl font-bold mb-6 text-yellow-200 drop-shadow-lg">
              {t('websiteFullTitle')}
            </h2>
            <p className="text-xl md:text-2xl mb-10 text-gray-100 leading-relaxed drop-shadow-md max-w-4xl mx-auto">
              {t('fraPortalSubtitle')}
            </p>
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <button
                onClick={() => navigate('/login')}
                className="group px-10 py-5 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white rounded-2xl font-bold text-lg flex items-center justify-center gap-3 transition-all duration-300 shadow-2xl hover:shadow-orange-500/25 transform hover:scale-105 hover:-translate-y-2 border-2 border-orange-400/50"
              >
                <span>🚀</span>
                {t('getStarted')}
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/citizen-portal')}
                className="group px-10 py-5 bg-gradient-to-r from-teal-500 to-blue-600 hover:from-teal-600 hover:to-blue-700 text-white rounded-2xl font-bold text-lg transition-all duration-300 shadow-2xl hover:shadow-teal-500/25 transform hover:scale-105 hover:-translate-y-2 border-2 border-teal-400/50 backdrop-blur-sm"
              >
                <span>🗺️</span>
                {t('exploreAtlas')}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* What is FRA Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Scale className="w-16 h-16 mx-auto text-green-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('whatIsFRA')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('fraDefinition')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <div className="text-center">
              <BookOpen className="w-12 h-12 mx-auto text-blue-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{t('legislation')}</h3>
              <p className="text-gray-600">{t('legislationDesc')}</p>
            </div>
            <div className="text-center">
              <Users className="w-12 h-12 mx-auto text-green-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{t('coverage')}</h3>
              <p className="text-gray-600">{t('coverageDesc')}</p>
            </div>
            <div className="text-center">
              <CheckCircle className="w-12 h-12 mx-auto text-purple-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{t('objective')}</h3>
              <p className="text-gray-600">{t('objectiveDesc')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Problems We Address */}
      <div className="py-20 bg-gradient-to-br from-orange-50 via-red-50 to-pink-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <AlertTriangle className="w-16 h-16 mx-auto text-red-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('problemsWeAddress')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('problemsIntro')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {problems.map((problem, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 p-3 bg-red-100 rounded-full">
                    {problem.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">
                      {problem.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
                      {problem.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Our Solutions */}
      <div className="py-20 bg-gradient-to-br from-teal-50 via-cyan-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Zap className="w-16 h-16 mx-auto text-green-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('ourSolutions')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('solutionsIntro')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {solutions.map((solution, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 p-3 bg-green-100 rounded-full">
                    {solution.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">
                      {solution.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
                      {solution.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Unique Features */}
      <div className="py-20 bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <Award className="w-16 h-16 mx-auto text-blue-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('whatMakesUsUnique')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('uniqueIntro')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {uniqueFeatures.map((feature, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {feature.title}
                      </h3>
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
                        {feature.highlight}
                      </span>
                    </div>
                    <p className="text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <BarChart3 className="w-16 h-16 mx-auto text-purple-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('platformOverview')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('platformOverviewDesc')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const colors = [
                'from-emerald-500 to-teal-600',
                'from-blue-500 to-indigo-600', 
                'from-purple-500 to-pink-600',
                'from-orange-500 to-red-600'
              ];
              return (
                <div key={index} className="text-center bg-white p-8 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2 border border-gray-100">
                  <div className="mb-6 flex justify-center">
                    <div className={`p-4 bg-gradient-to-br ${colors[index]} rounded-2xl shadow-lg`}>
                      <div className="text-white">
                        {stat.icon}
                      </div>
                    </div>
                  </div>
                  <div className="text-4xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent mb-3">{stat.value}</div>
                  <div className="text-lg font-semibold text-gray-700 mb-2">{stat.label}</div>
                  <div className="text-sm text-gray-500">{stat.description}</div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <TreePine className="w-16 h-16 mx-auto text-green-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('keyFeatures')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('keyFeaturesDesc')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                onClick={() => navigate(feature.path)}
                className={`${feature.color} p-8 rounded-xl cursor-pointer transition-all duration-300 hover:shadow-lg border border-gray-200 hover:-translate-y-1`}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {feature.icon}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 mb-4 leading-relaxed">
                      {feature.description}
                    </p>
                    <div className="flex items-center text-sm font-medium text-gray-700 hover:text-gray-900">
                      {t('learnMore')}
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Regions Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <MapPin className="w-16 h-16 mx-auto text-orange-600 mb-6" />
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              {t('coveredRegions')}
            </h2>
            <p className="text-xl text-gray-600 max-w-4xl mx-auto leading-relaxed">
              {t('coveredRegionsDesc')}
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              { name: t('madhyaPradesh'), tribes: t('gondiTribes'), color: 'bg-green-100 text-green-800', population: '15.3M' },
              { name: t('tripura'), tribes: t('kokborokPeople'), color: 'bg-blue-100 text-blue-800', population: '1.2M' },
              { name: t('odisha'), tribes: t('santaliTribes'), color: 'bg-purple-100 text-purple-800', population: '9.6M' },
              { name: t('telangana'), tribes: t('kolamTribal'), color: 'bg-orange-100 text-orange-800', population: '3.2M' }
            ].map((region, index) => (
              <div key={index} className="text-center p-8 rounded-xl border border-gray-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white">
                <div className="mb-6">
                  <MapPin className="w-12 h-12 mx-auto text-gray-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{region.name}</h3>
                <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${region.color} mb-3`}>
                  {region.tribes}
                </span>
                <div className="text-2xl font-bold text-gray-900">{region.population}</div>
                <div className="text-sm text-gray-500">{t('tribalPopulation')}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-20 bg-gradient-to-br from-orange-600 via-red-600 to-pink-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="max-w-4xl mx-auto text-center px-6 relative z-10">
          <div className="mb-8">
            <div className="inline-block px-6 py-3 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6">
              <span className="text-yellow-200 font-bold text-xl">🌟 Join the Movement</span>
            </div>
          </div>
          <h2 className="text-5xl font-extrabold text-white mb-8 drop-shadow-2xl">
            {t('readyToStart')}
          </h2>
          <p className="text-xl text-gray-100 mb-12 leading-relaxed drop-shadow-md max-w-3xl mx-auto">
            {t('readyToStartDesc')}
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <button
              onClick={() => navigate('/login')}
              className="group px-12 py-5 bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-black rounded-2xl font-bold text-lg transition-all duration-300 hover:shadow-2xl hover:shadow-yellow-500/25 transform hover:scale-105 hover:-translate-y-2 border-2 border-yellow-300/50"
            >
              <span>⚡</span>
              {t('startManagingCases')}
            </button>
            <button
              onClick={() => navigate('/login')}
              className="group px-12 py-5 bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-600 hover:to-indigo-700 text-white rounded-2xl font-bold text-lg transition-all duration-300 hover:shadow-2xl hover:shadow-purple-500/25 transform hover:scale-105 hover:-translate-y-2 border-2 border-purple-400/50 backdrop-blur-sm"
            >
              <span>📊</span>
              {t('viewDashboard')}
            </button>
          </div>
        </div>
        
        {/* Decorative Elements */}
        <div className="absolute top-10 left-10 w-20 h-20 bg-white/5 rounded-full blur-xl"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-white/5 rounded-full blur-2xl"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 bg-yellow-400/10 rounded-full blur-lg"></div>
      </div>
    </div>
  );
};

export default Home;