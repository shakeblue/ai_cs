/**
 * 로깅 설정
 * Winston을 사용한 구조화된 로깅
 */

const winston = require('winston');
const path = require('path');

// 로그 레벨 정의
const _v_log_levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4,
};

// 환경변수에서 로그 레벨 가져오기
const _v_level = process.env.LOG_LEVEL || 'info';

// 로그 색상 설정
const _v_colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'blue',
};

winston.addColors(_v_colors);

// 로그 포맷 정의
const _v_format = winston.format.combine(
  // 타임스탬프 추가
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  
  // 에러 스택 추가
  winston.format.errors({ stack: true }),
  
  // JSON 형식으로 변환
  winston.format.json(),
  
  // 커스텀 포맷
  winston.format.printf((p_info) => {
    const _v_message = typeof p_info.message === 'object' 
      ? JSON.stringify(p_info.message) 
      : p_info.message;
    
    let _v_log = `[${p_info.timestamp}] ${p_info.level.toUpperCase()}: ${_v_message}`;
    
    // 추가 메타데이터가 있으면 출력
    if (Object.keys(p_info).length > 4) {
      const _v_meta = { ...p_info };
      delete _v_meta.timestamp;
      delete _v_meta.level;
      delete _v_meta.message;
      delete _v_meta[Symbol.for('level')];
      _v_log += ` ${JSON.stringify(_v_meta)}`;
    }
    
    return _v_log;
  })
);

// 콘솔 출력 포맷 (색상 포함)
const _v_console_format = winston.format.combine(
  winston.format.colorize({ all: true }),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf((p_info) => {
    const _v_message = typeof p_info.message === 'object' 
      ? JSON.stringify(p_info.message) 
      : p_info.message;
    return `[${p_info.timestamp}] ${p_info.level}: ${_v_message}`;
  })
);

// Transport 설정
const _v_transports = [
  // 콘솔 출력
  new winston.transports.Console({
    format: _v_console_format,
  }),
  
  // 에러 로그 파일
  new winston.transports.File({
    filename: path.join(process.env.LOG_FILE_PATH || './logs', 'error.log'),
    level: 'error',
    format: _v_format,
    maxsize: 5242880, // 5MB
    maxFiles: 5,
  }),
  
  // 전체 로그 파일
  new winston.transports.File({
    filename: path.join(process.env.LOG_FILE_PATH || './logs', 'combined.log'),
    format: _v_format,
    maxsize: 5242880, // 5MB
    maxFiles: 5,
  }),
];

// Winston 로거 생성
const logger = winston.createLogger({
  level: _v_level,
  levels: _v_log_levels,
  format: _v_format,
  transports: _v_transports,
  exitOnError: false,
});

// HTTP 요청 로깅을 위한 Morgan 스트림
logger.stream = {
  write: (p_message) => {
    logger.http(p_message.trim());
  },
};

module.exports = logger;


