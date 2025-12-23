/**
 * ChatMessage Component
 * Individual chat message display with user nickname, message, and timestamp
 */
import React from 'react';
import { Box, Typography, Stack, Chip, alpha } from '@mui/material';
import {
  ChatBubble as ChatIcon,
  Announcement as AnnouncementIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

// Dark theme colors
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  primary: '#6366F1',
  warning: '#F59E0B',
  info: '#3B82F6',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
  border: '#2D3748',
  chat: {
    messageBg: '#1E293B',
    userColor: '#6366F1',
    systemColor: '#F59E0B',
    timestampColor: '#64748B',
  },
};

const ChatMessage = ({ message }) => {
  const { nickname, message: text, created_at_source, comment_type } = message;

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  // Determine message type styling
  const getMessageStyle = () => {
    switch (comment_type?.toLowerCase()) {
      case 'system':
        return {
          bgColor: alpha(DARK_COLORS.warning, 0.1),
          borderColor: DARK_COLORS.warning,
          icon: <InfoIcon fontSize="small" sx={{ color: DARK_COLORS.warning }} />,
        };
      case 'announcement':
        return {
          bgColor: alpha(DARK_COLORS.info, 0.1),
          borderColor: DARK_COLORS.info,
          icon: <AnnouncementIcon fontSize="small" sx={{ color: DARK_COLORS.info }} />,
        };
      default:
        return {
          bgColor: DARK_COLORS.chat.messageBg,
          borderColor: DARK_COLORS.border,
          icon: <ChatIcon fontSize="small" sx={{ color: DARK_COLORS.chat.userColor }} />,
        };
    }
  };

  const style = getMessageStyle();

  return (
    <Box
      sx={{
        p: 1.5,
        bgcolor: style.bgColor,
        borderLeft: `3px solid ${style.borderColor}`,
        borderRadius: 1,
        transition: 'all 0.2s ease',
        '&:hover': {
          bgcolor: alpha(style.borderColor, 0.15),
        },
      }}
    >
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
        <Stack direction="row" spacing={1} alignItems="center" sx={{ flex: 1 }}>
          {style.icon}
          <Typography
            variant="body2"
            sx={{
              color: DARK_COLORS.chat.userColor,
              fontWeight: 600,
            }}
          >
            {nickname || 'Anonymous'}
          </Typography>
          {comment_type && comment_type !== 'regular' && (
            <Chip
              label={comment_type}
              size="small"
              sx={{
                height: 18,
                fontSize: '0.65rem',
                bgcolor: style.borderColor,
                color: 'white',
              }}
            />
          )}
        </Stack>

        <Typography
          variant="caption"
          sx={{
            color: DARK_COLORS.chat.timestampColor,
            fontSize: '0.7rem',
            whiteSpace: 'nowrap',
            ml: 2,
          }}
        >
          {formatTime(created_at_source)}
        </Typography>
      </Stack>

      <Typography
        variant="body2"
        sx={{
          color: DARK_COLORS.text.primary,
          mt: 0.5,
          ml: 3,
          wordBreak: 'break-word',
        }}
      >
        {text}
      </Typography>
    </Box>
  );
};

export default ChatMessage;
