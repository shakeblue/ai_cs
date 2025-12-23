/**
 * useBroadcastDetail Hook
 * Fetches single broadcast details with all related data
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

const getApiBaseUrl = () => {
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  return baseUrl.replace(/\/api\/?$/, '');
};

const API_BASE_URL = getApiBaseUrl();

export const useBroadcastDetail = (broadcastId) => {
  const [broadcast, setBroadcast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBroadcast = async () => {
      if (!broadcastId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        console.log('🔍 Fetching broadcast detail:', broadcastId);

        const response = await axios.get(`${API_BASE_URL}/api/broadcasts/${broadcastId}`);

        console.log('✅ Broadcast detail fetched:', response.data);

        if (response.data) {
          setBroadcast(response.data);
        } else {
          setBroadcast(null);
        }
      } catch (err) {
        console.error('❌ Error fetching broadcast detail:', err);
        setError(err);
        setBroadcast(null);
      } finally {
        setLoading(false);
      }
    };

    fetchBroadcast();
  }, [broadcastId]);

  return { broadcast, loading, error };
};

export default useBroadcastDetail;
