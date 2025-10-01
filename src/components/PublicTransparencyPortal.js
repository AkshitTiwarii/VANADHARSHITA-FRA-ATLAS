import React, { useState, useEffect } from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { 
  BarChart3,
  Download,
  MapPin,
  TrendingUp,
  Users,
  TreePine,
  Shield,
  FileBarChart,
  Calendar,
  Filter,
  Info,
  ExternalLink
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const PublicTransparencyPortal = () => {
  const { t } = useTranslation();
  const [selectedState, setSelectedState] = useState('all');
  const [selectedYear, setSelectedYear] = useState('2024');
  const [viewType, setViewType] = useState('overview');

  // Aggregated public data (anonymized)
  const transparencyData = {
    overview: {
      totalClaims: 15847,
      approvedClaims: 12365,
      pendingClaims: 2892,
      rejectedClaims: 590,
      totalLandArea: 234567.8, // hectares
      totalBudget: 45678900000, // rupees
      budgetUtilized: 32456700000
    },
    stateWise: [
      {
        state: 'Madhya Pradesh',
        code: 'MP',
        totalClaims: 4256,
        approved: 3402,
        pending: 698,
        rejected: 156,
        landArea: 67890.2,
        budget: 12500000000,
        utilized: 9850000000,
        tribalPopulation: 1537652
      },
      {
        state: 'Telangana',
        code: 'TG',
        totalClaims: 3892,
        approved: 3156,
        pending: 578,
        rejected: 158,
        landArea: 45632.1,
        budget: 9800000000,
        utilized: 7650000000,
        tribalPopulation: 1089023
      },
      {
        state: 'Odisha',
        code: 'OR',
        totalClaims: 4567,
        approved: 3789,
        pending: 612,
        rejected: 166,
        landArea: 78456.3,
        budget: 15600000000,
        utilized: 11200000000,
        tribalPopulation: 2145678
      },
      {
        state: 'Tripura',
        code: 'TR',
        totalClaims: 3132,
        approved: 2018,
        pending: 1004,
        rejected: 110,
        landArea: 42589.2,
        budget: 7778900000,
        utilized: 3756700000,
        tribalPopulation: 993426
      }
    ],
    monthlyTrends: {
      2024: {
        claimsSubmitted: [145, 167, 189, 201, 234, 198, 176, 189, 223, 245, 267, 189],
        claimsApproved: [123, 134, 156, 178, 189, 167, 145, 156, 189, 201, 178, 123],
        budgetDisbursed: [125, 134, 167, 189, 234, 201, 156, 178, 198, 223, 201, 145] // in crores
      }
    },
    claimTypes: [
      { type: 'Individual Forest Rights', count: 8456, percentage: 53.4 },
      { type: 'Community Forest Rights', count: 4123, percentage: 26.0 },
      { type: 'Community Resource Rights', count: 2234, percentage: 14.1 },
      { type: 'Development Rights', count: 1034, percentage: 6.5 }
    ],
    processingMetrics: {
      avgProcessingTime: 45, // days
      fastestClaim: 12, // days
      slowestClaim: 287, // days
      onTimeDelivery: 78.5 // percentage
    }
  };

  const getApprovalRate = (approved, total) => {
    return ((approved / total) * 100).toFixed(1);
  };

  const getBudgetUtilization = (utilized, budget) => {
    return ((utilized / budget) * 100).toFixed(1);
  };

  const formatCurrency = (amount) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(1)}Cr`;
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(1)}L`;
    } else {
      return `₹${amount.toLocaleString()}`;
    }
  };

  const downloadReport = (type) => {
    // Generate downloadable reports
    console.log(`Downloading ${type} report`);
  };

  const openDataAPI = () => {
    // Link to public API documentation
    window.open('/api/docs', '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-2">{t('publicTransparencyPortal')}</h1>
            <p className="text-lg opacity-90">{t('transparentAccessToFRAData')}</p>
            <p className="text-sm opacity-75 mt-2">
              {t('lastUpdated')}: {new Date().toLocaleDateString()} | {t('dataProtected')}
            </p>
          </div>
        </div>
      </div>

      {/* Key Statistics */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 font-medium">{t('totalClaims')}</p>
                  <p className="text-3xl font-bold text-blue-800">{transparencyData.overview.totalClaims.toLocaleString()}</p>
                  <p className="text-xs text-blue-600 mt-1">
                    {getApprovalRate(transparencyData.overview.approvedClaims, transparencyData.overview.totalClaims)}% {t('approved')}
                  </p>
                </div>
                <FileBarChart className="w-10 h-10 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 font-medium">{t('landSecured')}</p>
                  <p className="text-3xl font-bold text-green-800">{(transparencyData.overview.totalLandArea / 1000).toFixed(0)}K</p>
                  <p className="text-xs text-green-600 mt-1">{t('hectares')}</p>
                </div>
                <TreePine className="w-10 h-10 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-600 font-medium">{t('budgetAllocated')}</p>
                  <p className="text-3xl font-bold text-purple-800">{formatCurrency(transparencyData.overview.totalBudget)}</p>
                  <p className="text-xs text-purple-600 mt-1">
                    {getBudgetUtilization(transparencyData.overview.budgetUtilized, transparencyData.overview.totalBudget)}% {t('utilized')}
                  </p>
                </div>
                <BarChart3 className="w-10 h-10 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-600 font-medium">{t('avgProcessingTime')}</p>
                  <p className="text-3xl font-bold text-orange-800">{transparencyData.processingMetrics.avgProcessingTime}</p>
                  <p className="text-xs text-orange-600 mt-1">{t('days')}</p>
                </div>
                <TrendingUp className="w-10 h-10 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* State-wise Performance */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              {t('stateWisePerformance')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">{t('state')}</th>
                    <th className="text-right py-3 px-4 font-medium">{t('totalClaims')}</th>
                    <th className="text-right py-3 px-4 font-medium">{t('approvalRate')}</th>
                    <th className="text-right py-3 px-4 font-medium">{t('landArea')} (ha)</th>
                    <th className="text-right py-3 px-4 font-medium">{t('budgetUtilization')}</th>
                    <th className="text-right py-3 px-4 font-medium">{t('tribalPopulation')}</th>
                  </tr>
                </thead>
                <tbody>
                  {transparencyData.stateWise.map((state) => (
                    <tr key={state.code} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{state.code}</Badge>
                          <span className="font-medium">{state.state}</span>
                        </div>
                      </td>
                      <td className="text-right py-3 px-4 font-medium">{state.totalClaims.toLocaleString()}</td>
                      <td className="text-right py-3 px-4">
                        <span className={`font-medium ${
                          getApprovalRate(state.approved, state.totalClaims) > 80 ? 'text-green-600' :
                          getApprovalRate(state.approved, state.totalClaims) > 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {getApprovalRate(state.approved, state.totalClaims)}%
                        </span>
                      </td>
                      <td className="text-right py-3 px-4">{state.landArea.toLocaleString()}</td>
                      <td className="text-right py-3 px-4">
                        <span className={`font-medium ${
                          getBudgetUtilization(state.utilized, state.budget) > 80 ? 'text-green-600' :
                          getBudgetUtilization(state.utilized, state.budget) > 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          {getBudgetUtilization(state.utilized, state.budget)}%
                        </span>
                      </td>
                      <td className="text-right py-3 px-4">{state.tribalPopulation.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Claim Types Distribution */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>{t('claimTypesDistribution')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {transparencyData.claimTypes.map((type) => (
                  <div key={type.type} className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">{t(type.type.toLowerCase().replace(/\s+/g, ''))}</span>
                        <span className="text-sm text-gray-600">{type.percentage}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${type.percentage}%` }}
                        ></div>
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{type.count.toLocaleString()} {t('claims')}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('processingMetrics')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('avgProcessingTime')}</span>
                  <span className="font-bold">{transparencyData.processingMetrics.avgProcessingTime} {t('days')}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('fastestProcessing')}</span>
                  <span className="font-bold text-green-600">{transparencyData.processingMetrics.fastestClaim} {t('days')}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('slowestProcessing')}</span>
                  <span className="font-bold text-red-600">{transparencyData.processingMetrics.slowestClaim} {t('days')}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('onTimeDelivery')}</span>
                  <span className="font-bold text-blue-600">{transparencyData.processingMetrics.onTimeDelivery}%</span>
                </div>

                <div className="pt-4 border-t">
                  <div className="text-sm text-gray-600 mb-2">{t('performanceTrend')}</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${transparencyData.processingMetrics.onTimeDelivery}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Data Access and Downloads */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="w-5 h-5" />
              {t('dataAccessAndDownloads')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">{t('reports')}</h3>
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => downloadReport('monthly')}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {t('monthlyReport')}
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => downloadReport('annual')}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {t('annualReport')}
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => downloadReport('state-wise')}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    {t('stateWiseReport')}
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">{t('datasets')}</h3>
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => downloadReport('aggregated-claims')}
                  >
                    <FileBarChart className="w-4 h-4 mr-2" />
                    {t('aggregatedClaimsData')}
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => downloadReport('budget-utilization')}
                  >
                    <BarChart3 className="w-4 h-4 mr-2" />
                    {t('budgetUtilizationData')}
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={() => downloadReport('performance-metrics')}
                  >
                    <TrendingUp className="w-4 h-4 mr-2" />
                    {t('performanceMetrics')}
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900">{t('apiAccess')}</h3>
                <div className="space-y-2">
                  <Button 
                    variant="outline" 
                    className="w-full justify-start"
                    onClick={openDataAPI}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    {t('apiDocumentation')}
                  </Button>
                  <div className="text-xs text-gray-600 p-3 bg-gray-50 rounded-lg">
                    <p className="font-medium mb-1">{t('dataPrivacyNotice')}</p>
                    <p>{t('dataPrivacyDescription')}</p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <div className="mt-8 pt-6 border-t text-center text-sm text-gray-600">
          <p>{t('transparencyFooter')}</p>
          <p className="mt-2">
            {t('dataSourceDisclaimer')} | 
            <a href="/privacy-policy" className="text-blue-600 hover:underline ml-1">{t('privacyPolicy')}</a> |
            <a href="/terms" className="text-blue-600 hover:underline ml-1">{t('terms')}</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PublicTransparencyPortal;