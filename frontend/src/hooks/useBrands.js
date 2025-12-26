/**
 * useBrands Hook
 * Fetches list of unique brands from broadcasts
 */
import { useState, useEffect } from 'react';
import axios from 'axios';

const getApiBaseUrl = () => {
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  return baseUrl.replace(/\/api\/?$/, '');
};

const API_BASE_URL = getApiBaseUrl();

export const useBrands = () => {
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBrands = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('🔍 Fetching brands:', `${API_BASE_URL}/api/broadcasts/brands`);

        const response = await axios.get(`${API_BASE_URL}/api/broadcasts/brands`);

        console.log('✅ Brands fetched:', response.data);

        if (response.data && response.data.data) {
          setBrands(response.data.data);
        } else {
          setBrands([]);
        }
      } catch (err) {
        console.error('❌ Error fetching brands:', err);
        setError(err);
        setBrands([]);
      } finally {
        setLoading(false);
      }
    };

    fetchBrands();
  }, []);

  return { brands, loading, error };
};

export default useBrands;
