import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Filter, Calendar, Building2, Tag, ExternalLink, RefreshCw, Activity } from 'lucide-react';
import { format } from 'date-fns';
import './App.css';

function App() {
  const [guidelines, setGuidelines] = useState([]);
  const [filteredGuidelines, setFilteredGuidelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [selectedSpecialty, setSelectedSpecialty] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [sources, setSources] = useState([]);
  const [specialties, setSpecialties] = useState([]);
  const [stats, setStats] = useState({});
  const [lastUpdated, setLastUpdated] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Filter guidelines when search or filters change
  useEffect(() => {
    filterGuidelines();
  }, [guidelines, searchTerm, selectedSource, selectedSpecialty, selectedYear]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch guidelines, sources, specialties, and stats in parallel
      const [guidelinesRes, sourcesRes, specialtiesRes, statsRes] = await Promise.all([
        axios.get('/api/guidelines'),
        axios.get('/api/sources'),
        axios.get('/api/specialties'),
        axios.get('/api/stats')
      ]);

      setGuidelines(guidelinesRes.data.guidelines);
      setFilteredGuidelines(guidelinesRes.data.guidelines);
      setSources(sourcesRes.data.sources);
      setSpecialties(specialtiesRes.data.specialties);
      setStats(statsRes.data);
      setLastUpdated(guidelinesRes.data.last_updated);
      
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterGuidelines = () => {
    let filtered = [...guidelines];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(guideline =>
        guideline.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        guideline.summary.toLowerCase().includes(searchTerm.toLowerCase()) ||
        guideline.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filter by source
    if (selectedSource) {
      filtered = filtered.filter(guideline => guideline.source === selectedSource);
    }

    // Filter by specialty
    if (selectedSpecialty) {
      filtered = filtered.filter(guideline =>
        guideline.tags.some(tag => tag.toLowerCase().includes(selectedSpecialty.toLowerCase()))
      );
    }

    // Filter by year
    if (selectedYear) {
      filtered = filtered.filter(guideline => {
        const guidelineYear = new Date(guideline.date).getFullYear().toString();
        return guidelineYear === selectedYear;
      });
    }

    setFilteredGuidelines(filtered);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedSource('');
    setSelectedSpecialty('');
    setSelectedYear('');
  };

  const getSourceBadgeClass = (source) => {
    const sourceLower = source.toLowerCase();
    switch (sourceLower) {
      case 'who': return 'badge-who';
      case 'cdc': return 'badge-cdc';
      case 'nice': return 'badge-nice';
      case 'aha': return 'badge-aha';
      case 'ada': return 'badge-ada';
      case 'idsa': return 'badge-idsa';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return dateString;
    }
  };

  const getYears = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let year = currentYear; year >= currentYear - 10; year--) {
      years.push(year.toString());
    }
    return years;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading medical guidelines...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-medical-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Global Medical Guidelines AI Hub</h1>
                <p className="text-sm text-gray-500">
                  Real-time clinical practice guidelines from leading medical organizations
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={fetchData}
                className="btn-secondary flex items-center space-x-2"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="bg-medical-50 border-b border-medical-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap items-center justify-between text-sm">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <Building2 className="w-4 h-4 text-medical-600" />
                <span className="text-medical-700">
                  <span className="font-semibold">{stats.total_guidelines || 0}</span> guidelines
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4 text-medical-600" />
                <span className="text-medical-700">
                  <span className="font-semibold">{stats.recent_guidelines || 0}</span> recent (30 days)
                </span>
              </div>
            </div>
            {lastUpdated && (
              <div className="text-medical-600">
                Last updated: {formatDate(lastUpdated)}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="mb-8">
          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search guidelines by title, content, or tags..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10 pr-4 py-3 text-lg"
            />
          </div>

          {/* Filter Toggle */}
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="btn-secondary flex items-center space-x-2"
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
            
            {(searchTerm || selectedSource || selectedSpecialty || selectedYear) && (
              <button
                onClick={clearFilters}
                className="text-medical-600 hover:text-medical-700 text-sm font-medium"
              >
                Clear all filters
              </button>
            )}
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="card p-6 mb-6 animate-slide-up">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Source Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organization
                  </label>
                  <select
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value)}
                    className="input-field"
                  >
                    <option value="">All Organizations</option>
                    {sources.map(source => (
                      <option key={source} value={source}>{source}</option>
                    ))}
                  </select>
                </div>

                {/* Specialty Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Specialty
                  </label>
                  <select
                    value={selectedSpecialty}
                    onChange={(e) => setSelectedSpecialty(e.target.value)}
                    className="input-field"
                  >
                    <option value="">All Specialties</option>
                    {specialties.map(specialty => (
                      <option key={specialty} value={specialty}>{specialty}</option>
                    ))}
                  </select>
                </div>

                {/* Year Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Year
                  </label>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(e.target.value)}
                    className="input-field"
                  >
                    <option value="">All Years</option>
                    {getYears().map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-gray-600">
            Showing <span className="font-semibold">{filteredGuidelines.length}</span> of{' '}
            <span className="font-semibold">{guidelines.length}</span> guidelines
          </p>
        </div>

        {/* Guidelines Grid */}
        {filteredGuidelines.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No guidelines found</h3>
            <p className="text-gray-500">
              Try adjusting your search terms or filters to find what you're looking for.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredGuidelines.map((guideline) => (
              <div key={guideline.id} className="card p-6 hover:shadow-lg transition-shadow duration-200">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <span className={`badge ${getSourceBadgeClass(guideline.source)}`}>
                    {guideline.source}
                  </span>
                  <span className="text-sm text-gray-500">
                    {formatDate(guideline.date)}
                  </span>
                </div>

                {/* Title */}
                <h3 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2">
                  {guideline.title}
                </h3>

                {/* Summary */}
                <div className="mb-4">
                  <p className="text-gray-600 text-sm leading-relaxed line-clamp-4">
                    {guideline.summary}
                  </p>
                </div>

                {/* Tags */}
                {guideline.tags && guideline.tags.length > 0 && (
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-1">
                      {guideline.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                        >
                          <Tag className="w-3 h-3 mr-1" />
                          {tag}
                        </span>
                      ))}
                      {guideline.tags.length > 3 && (
                        <span className="text-xs text-gray-500">
                          +{guideline.tags.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Button */}
                <a
                  href={guideline.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary w-full flex items-center justify-center space-x-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Read Full Guideline</span>
                </a>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App; 