/**
 * ChatList Component
 * Displays all chat messages with search, sort, and export functionality
 */
import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Paper,
  Chip,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  GetApp as ExportIcon,
} from '@mui/icons-material';
import ChatMessage from './ChatMessage';

// Dark theme colors
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
  border: '#2D3748',
};

const ChatList = ({ messages, broadcastId }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' or 'desc'

  // Filter and sort messages
  const filteredMessages = useMemo(() => {
    let filtered = messages || [];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(
        (msg) =>
          msg.message?.toLowerCase().includes(searchQuery.toLowerCase()) ||
          msg.nickname?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Sort by timestamp
    const sorted = [...filtered].sort((a, b) => {
      const dateA = new Date(a.created_at_source || a.created_at);
      const dateB = new Date(b.created_at_source || b.created_at);
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });

    return sorted;
  }, [messages, searchQuery, sortOrder]);

  const handleExport = () => {
    // Export chat to JSON
    const dataStr = JSON.stringify(filteredMessages, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = `broadcast_${broadcastId}_chat.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  return (
    <Box>
      {/* Controls */}
      <Stack
        direction="row"
        spacing={2}
        sx={{ mb: 3, alignItems: 'center', flexWrap: 'wrap' }}
      >
        <TextField
          placeholder="Search messages or users..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{
            flex: 1,
            minWidth: 250,
            '& .MuiOutlinedInput-root': {
              bgcolor: DARK_COLORS.cardBg,
              color: DARK_COLORS.text.primary,
              '& fieldset': {
                borderColor: DARK_COLORS.border,
              },
              '&:hover fieldset': {
                borderColor: DARK_COLORS.text.secondary,
              },
            },
          }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: DARK_COLORS.text.secondary }} />
              </InputAdornment>
            ),
          }}
        />

        <FormControl
          size="small"
          sx={{
            minWidth: 150,
            '& .MuiOutlinedInput-root': {
              bgcolor: DARK_COLORS.cardBg,
              color: DARK_COLORS.text.primary,
              '& fieldset': {
                borderColor: DARK_COLORS.border,
              },
            },
            '& .MuiInputLabel-root': {
              color: DARK_COLORS.text.secondary,
            },
          }}
        >
          <InputLabel>Sort Order</InputLabel>
          <Select
            value={sortOrder}
            label="Sort Order"
            onChange={(e) => setSortOrder(e.target.value)}
          >
            <MenuItem value="desc">Newest First</MenuItem>
            <MenuItem value="asc">Oldest First</MenuItem>
          </Select>
        </FormControl>

        <Chip
          label={`${filteredMessages.length} messages`}
          color="primary"
          variant="outlined"
          sx={{ color: DARK_COLORS.text.primary }}
        />

        <IconButton
          onClick={handleExport}
          title="Export to JSON"
          sx={{ color: DARK_COLORS.text.primary }}
        >
          <ExportIcon />
        </IconButton>
      </Stack>

      {/* Message List */}
      <Paper
        sx={{
          bgcolor: DARK_COLORS.cardBg,
          p: 2,
          maxHeight: 600,
          overflowY: 'auto',
          border: `1px solid ${DARK_COLORS.border}`,
          borderRadius: 2,
        }}
      >
        {filteredMessages.length === 0 ? (
          <Typography
            variant="body2"
            color={DARK_COLORS.text.secondary}
            sx={{ textAlign: 'center', py: 4 }}
          >
            {searchQuery ? 'No messages found' : 'No chat messages available'}
          </Typography>
        ) : (
          <Stack spacing={1}>
            {filteredMessages.map((message, index) => (
              <ChatMessage key={message.id || index} message={message} />
            ))}
          </Stack>
        )}
      </Paper>
    </Box>
  );
};

export default ChatList;
