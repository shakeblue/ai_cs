/**
 * useBroadcasts Hook
 * Fetches broadcast list with pagination and filters
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

const getApiBaseUrl = () => {
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  return baseUrl.replace(/\/api\/?$/, '');
};

const API_BASE_URL = getApiBaseUrl();

export const useBroadcasts = ({ page = 1, limit = 20, search = '', brand = '', status = '', broadcastType = '', startDate = '', endDate = '', sortBy = 'date_desc' }) => {
  const [broadcasts, setBroadcasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0,
  });

  useEffect(() => {
    const fetchBroadcasts = async () => {
      try {
        setLoading(true);
        setError(null);

        // Build query params
        const params = new URLSearchParams({
          page: page.toString(),
          limit: limit.toString(),
        });

        if (search) params.append('search', search);
        if (brand) params.append('brand', brand);
        if (status) params.append('status', status);
        if (broadcastType) params.append('broadcast_type', broadcastType);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (sortBy) params.append('sort', sortBy);

        console.log('🔍 Fetching broadcasts:', `${API_BASE_URL}/api/broadcasts?${params}`);

        const response = await axios.get(`${API_BASE_URL}/api/broadcasts?${params}`);

        console.log('✅ Broadcasts fetched:', response.data);

        if (response.data && response.data.data) {
          setBroadcasts(response.data.data);
          setPagination(response.data.pagination || {
            page,
            limit,
            total: response.data.data.length,
            pages: 1,
          });
        } else {
          setBroadcasts([]);
          setPagination({ page, limit, total: 0, pages: 0 });
        }
      } catch (err) {
        console.error('❌ Error fetching broadcasts:', err);
        setError(err);
        setBroadcasts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchBroadcasts();
  }, [page, limit, search, brand, status, broadcastType, startDate, endDate, sortBy]);

  const refetch = () => {
    setLoading(true);
  };

  return { broadcasts, loading, error, pagination, refetch };
};

export default useBroadcasts;
