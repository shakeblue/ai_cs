--
-- PostgreSQL database dump
--

\restrict YJWIEiB9YdJqwhVGQDRNnXGACWrsg2uYIujzTMj16coBhumeGvcMBkCuv1CeSEP

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: get_dashboard_stats(); Type: FUNCTION; Schema: public; Owner: cs_user
--

CREATE FUNCTION public.get_dashboard_stats() RETURNS json
    LANGUAGE plpgsql
    AS $$
DECLARE
    _v_result JSON;
BEGIN
    SELECT json_build_object(
        'total_active_events', (SELECT COUNT(*) FROM events WHERE status = 'ACTIVE'),
        'total_channels', (SELECT COUNT(*) FROM channels WHERE is_active = TRUE),
        'total_users', (SELECT COUNT(*) FROM users WHERE is_active = TRUE),
        'today_views', (SELECT COUNT(*) FROM view_logs WHERE DATE(viewed_at) = CURRENT_DATE),
        'channel_breakdown', (
            SELECT json_agg(row_to_json(t))
            FROM v_channel_statistics t
        ),
        'urgent_events', (
            SELECT json_agg(row_to_json(e))
            FROM (
                SELECT event_id, title, channel_name, end_date
                FROM v_active_events
                WHERE end_date BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '2 days'
                LIMIT 10
            ) e
        )
    ) INTO _v_result;
    
    RETURN _v_result;
END;
$$;


ALTER FUNCTION public.get_dashboard_stats() OWNER TO cs_user;

--
-- Name: log_event_changes(); Type: FUNCTION; Schema: public; Owner: cs_user
--

CREATE FUNCTION public.log_event_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    _v_change_type VARCHAR(20);
    _v_old_values JSONB;
    _v_new_values JSONB;
BEGIN
    IF TG_OP = 'INSERT' THEN
        _v_change_type = 'INSERT';
        _v_new_values = row_to_json(NEW)::JSONB;
        INSERT INTO event_history (event_id, change_type, new_values, changed_by)
        VALUES (NEW.event_id, _v_change_type, _v_new_values, 'system');
        
    ELSIF TG_OP = 'UPDATE' THEN
        _v_change_type = 'UPDATE';
        _v_old_values = row_to_json(OLD)::JSONB;
        _v_new_values = row_to_json(NEW)::JSONB;
        INSERT INTO event_history (event_id, change_type, old_values, new_values, changed_by)
        VALUES (NEW.event_id, _v_change_type, _v_old_values, _v_new_values, 'system');
        
    ELSIF TG_OP = 'DELETE' THEN
        _v_change_type = 'DELETE';
        _v_old_values = row_to_json(OLD)::JSONB;
        INSERT INTO event_history (event_id, change_type, old_values, changed_by)
        VALUES (OLD.event_id, _v_change_type, _v_old_values, 'system');
    END IF;
    
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.log_event_changes() OWNER TO cs_user;

--
-- Name: search_events(character varying, character varying[], character varying, integer, integer); Type: FUNCTION; Schema: public; Owner: cs_user
--

CREATE FUNCTION public.search_events(p_keyword character varying, p_channel_codes character varying[] DEFAULT NULL::character varying[], p_status character varying DEFAULT 'ACTIVE'::character varying, p_limit integer DEFAULT 20, p_offset integer DEFAULT 0) RETURNS TABLE(event_id uuid, title character varying, channel_name character varying, benefit_summary character varying, start_date timestamp without time zone, end_date timestamp without time zone, event_url text, relevance real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.event_id,
        e.title,
        c.channel_name,
        e.benefit_summary,
        e.start_date,
        e.end_date,
        e.event_url,
        GREATEST(
            similarity(e.title, p_keyword),
            similarity(e.benefit_summary, p_keyword)
        ) as relevance
    FROM events e
    INNER JOIN channels c ON e.channel_id = c.channel_id
    WHERE 
        (p_status IS NULL OR e.status = p_status)
        AND (p_channel_codes IS NULL OR c.channel_code = ANY(p_channel_codes))
        AND (
            e.title ILIKE '%' || p_keyword || '%'
            OR e.benefit_summary ILIKE '%' || p_keyword || '%'
            OR e.target_products ILIKE '%' || p_keyword || '%'
        )
    ORDER BY relevance DESC, e.priority DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;


ALTER FUNCTION public.search_events(p_keyword character varying, p_channel_codes character varying[], p_status character varying, p_limit integer, p_offset integer) OWNER TO cs_user;

--
-- Name: update_event_status(); Type: FUNCTION; Schema: public; Owner: cs_user
--

CREATE FUNCTION public.update_event_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- 시작일과 종료일을 기반으로 상태 자동 결정
    IF NEW.start_date > CURRENT_TIMESTAMP THEN
        NEW.status = 'PENDING';
    ELSIF NEW.end_date < CURRENT_TIMESTAMP THEN
        NEW.status = 'ENDED';
    ELSE
        NEW.status = 'ACTIVE';
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_event_status() OWNER TO cs_user;

--
-- Name: update_favorite_count(); Type: FUNCTION; Schema: public; Owner: cs_user
--

CREATE FUNCTION public.update_favorite_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE events SET favorite_count = favorite_count + 1 WHERE event_id = NEW.event_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE events SET favorite_count = favorite_count - 1 WHERE event_id = OLD.event_id;
    END IF;
    RETURN NULL;
END;
$$;


ALTER FUNCTION public.update_favorite_count() OWNER TO cs_user;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: cs_user
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO cs_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: channels; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.channels (
    channel_id integer NOT NULL,
    channel_code character varying(50) NOT NULL,
    channel_name character varying(100) NOT NULL,
    channel_type character varying(20) NOT NULL,
    base_url text NOT NULL,
    crawl_interval integer DEFAULT 360,
    is_active boolean DEFAULT true,
    icon_url text,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_channel_type CHECK (((channel_type)::text = ANY ((ARRAY['DIRECT'::character varying, 'PARTNER'::character varying, 'LIVE'::character varying])::text[])))
);


ALTER TABLE public.channels OWNER TO cs_user;

--
-- Name: channels_channel_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.channels_channel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.channels_channel_id_seq OWNER TO cs_user;

--
-- Name: channels_channel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.channels_channel_id_seq OWNED BY public.channels.channel_id;


--
-- Name: crawl_logs; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.crawl_logs (
    log_id bigint NOT NULL,
    channel_id integer NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    duration_ms integer,
    items_found integer DEFAULT 0,
    items_new integer DEFAULT 0,
    items_updated integer DEFAULT 0,
    items_failed integer DEFAULT 0,
    error_message text,
    error_stack text,
    crawler_version character varying(20),
    metadata jsonb,
    CONSTRAINT chk_crawl_status CHECK (((status)::text = ANY ((ARRAY['SUCCESS'::character varying, 'FAILED'::character varying, 'PARTIAL'::character varying])::text[])))
);


ALTER TABLE public.crawl_logs OWNER TO cs_user;

--
-- Name: crawl_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.crawl_logs_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.crawl_logs_log_id_seq OWNER TO cs_user;

--
-- Name: crawl_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.crawl_logs_log_id_seq OWNED BY public.crawl_logs.log_id;


--
-- Name: event_history; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.event_history (
    history_id integer NOT NULL,
    event_id uuid NOT NULL,
    change_type character varying(20) NOT NULL,
    changed_fields jsonb,
    old_values jsonb,
    new_values jsonb,
    changed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    changed_by character varying(100),
    CONSTRAINT chk_change_type CHECK (((change_type)::text = ANY ((ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying])::text[])))
);


ALTER TABLE public.event_history OWNER TO cs_user;

--
-- Name: event_history_history_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.event_history_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_history_history_id_seq OWNER TO cs_user;

--
-- Name: event_history_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.event_history_history_id_seq OWNED BY public.event_history.history_id;


--
-- Name: events; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.events (
    event_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    channel_id integer NOT NULL,
    external_id character varying(255),
    title character varying(500) NOT NULL,
    subtitle character varying(500),
    description text,
    start_date timestamp without time zone NOT NULL,
    end_date timestamp without time zone NOT NULL,
    discount_rate numeric(5,2),
    discount_amount numeric(12,2),
    coupon_code character varying(100),
    benefit_summary character varying(500),
    benefit_detail text,
    target_products text,
    target_brands text,
    target_categories text,
    conditions text,
    cautions text,
    event_url text NOT NULL,
    image_url text,
    thumbnail_url text,
    status character varying(20) DEFAULT 'PENDING'::character varying,
    priority integer DEFAULT 0,
    view_count integer DEFAULT 0,
    favorite_count integer DEFAULT 0,
    tags text[],
    crawled_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_event_dates CHECK ((end_date >= start_date)),
    CONSTRAINT chk_event_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'ACTIVE'::character varying, 'ENDED'::character varying, 'CANCELLED'::character varying])::text[])))
);


ALTER TABLE public.events OWNER TO cs_user;

--
-- Name: favorites; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.favorites (
    favorite_id integer NOT NULL,
    user_id integer NOT NULL,
    event_id uuid NOT NULL,
    memo text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.favorites OWNER TO cs_user;

--
-- Name: favorites_favorite_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.favorites_favorite_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.favorites_favorite_id_seq OWNER TO cs_user;

--
-- Name: favorites_favorite_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.favorites_favorite_id_seq OWNED BY public.favorites.favorite_id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.system_settings (
    setting_id integer NOT NULL,
    setting_key character varying(100) NOT NULL,
    setting_value text,
    value_type character varying(20) DEFAULT 'STRING'::character varying,
    description text,
    is_editable boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_value_type CHECK (((value_type)::text = ANY ((ARRAY['STRING'::character varying, 'INTEGER'::character varying, 'BOOLEAN'::character varying, 'JSON'::character varying])::text[])))
);


ALTER TABLE public.system_settings OWNER TO cs_user;

--
-- Name: system_settings_setting_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.system_settings_setting_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_settings_setting_id_seq OWNER TO cs_user;

--
-- Name: system_settings_setting_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.system_settings_setting_id_seq OWNED BY public.system_settings.setting_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(255) NOT NULL,
    phone character varying(20),
    role character varying(20) DEFAULT 'AGENT'::character varying,
    department character varying(100),
    team character varying(100),
    is_active boolean DEFAULT true,
    last_login_at timestamp without time zone,
    login_count integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_role CHECK (((role)::text = ANY ((ARRAY['ADMIN'::character varying, 'AGENT'::character varying, 'VIEWER'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO cs_user;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO cs_user;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: v_active_events; Type: VIEW; Schema: public; Owner: cs_user
--

CREATE VIEW public.v_active_events AS
 SELECT e.event_id,
    e.title,
    e.subtitle,
    c.channel_name,
    c.channel_code,
    c.channel_type,
    e.start_date,
    e.end_date,
    e.discount_rate,
    e.benefit_summary,
    e.event_url,
    e.thumbnail_url,
    e.favorite_count,
    e.view_count,
    e.tags
   FROM (public.events e
     JOIN public.channels c ON ((e.channel_id = c.channel_id)))
  WHERE (((e.status)::text = 'ACTIVE'::text) AND (c.is_active = true))
  ORDER BY e.priority DESC, e.start_date DESC;


ALTER VIEW public.v_active_events OWNER TO cs_user;

--
-- Name: v_channel_statistics; Type: VIEW; Schema: public; Owner: cs_user
--

CREATE VIEW public.v_channel_statistics AS
 SELECT c.channel_id,
    c.channel_name,
    c.channel_type,
    count(e.event_id) AS total_events,
    count(
        CASE
            WHEN ((e.status)::text = 'ACTIVE'::text) THEN 1
            ELSE NULL::integer
        END) AS active_events,
    count(
        CASE
            WHEN ((e.status)::text = 'PENDING'::text) THEN 1
            ELSE NULL::integer
        END) AS pending_events,
    avg(e.discount_rate) AS avg_discount_rate,
    max(e.created_at) AS last_event_date
   FROM (public.channels c
     LEFT JOIN public.events e ON ((c.channel_id = e.channel_id)))
  WHERE (c.is_active = true)
  GROUP BY c.channel_id, c.channel_name, c.channel_type;


ALTER VIEW public.v_channel_statistics OWNER TO cs_user;

--
-- Name: v_popular_events; Type: VIEW; Schema: public; Owner: cs_user
--

CREATE VIEW public.v_popular_events AS
 SELECT e.event_id,
    e.title,
    c.channel_name,
    e.start_date,
    e.end_date,
    e.benefit_summary,
    e.favorite_count,
    e.view_count,
    ((e.favorite_count * 3) + e.view_count) AS popularity_score
   FROM (public.events e
     JOIN public.channels c ON ((e.channel_id = c.channel_id)))
  WHERE ((e.status)::text = 'ACTIVE'::text)
  ORDER BY ((e.favorite_count * 3) + e.view_count) DESC
 LIMIT 50;


ALTER VIEW public.v_popular_events OWNER TO cs_user;

--
-- Name: view_logs; Type: TABLE; Schema: public; Owner: cs_user
--

CREATE TABLE public.view_logs (
    log_id bigint NOT NULL,
    user_id integer,
    event_id uuid,
    view_type character varying(20) DEFAULT 'DETAIL'::character varying,
    ip_address inet,
    user_agent text,
    viewed_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_view_type CHECK (((view_type)::text = ANY ((ARRAY['LIST'::character varying, 'DETAIL'::character varying, 'CONSULTATION'::character varying])::text[])))
);


ALTER TABLE public.view_logs OWNER TO cs_user;

--
-- Name: view_logs_log_id_seq; Type: SEQUENCE; Schema: public; Owner: cs_user
--

CREATE SEQUENCE public.view_logs_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.view_logs_log_id_seq OWNER TO cs_user;

--
-- Name: view_logs_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cs_user
--

ALTER SEQUENCE public.view_logs_log_id_seq OWNED BY public.view_logs.log_id;


--
-- Name: channels channel_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.channels ALTER COLUMN channel_id SET DEFAULT nextval('public.channels_channel_id_seq'::regclass);


--
-- Name: crawl_logs log_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.crawl_logs ALTER COLUMN log_id SET DEFAULT nextval('public.crawl_logs_log_id_seq'::regclass);


--
-- Name: event_history history_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.event_history ALTER COLUMN history_id SET DEFAULT nextval('public.event_history_history_id_seq'::regclass);


--
-- Name: favorites favorite_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.favorites ALTER COLUMN favorite_id SET DEFAULT nextval('public.favorites_favorite_id_seq'::regclass);


--
-- Name: system_settings setting_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN setting_id SET DEFAULT nextval('public.system_settings_setting_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Name: view_logs log_id; Type: DEFAULT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.view_logs ALTER COLUMN log_id SET DEFAULT nextval('public.view_logs_log_id_seq'::regclass);


--
-- Name: channels channels_channel_code_key; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_channel_code_key UNIQUE (channel_code);


--
-- Name: channels channels_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.channels
    ADD CONSTRAINT channels_pkey PRIMARY KEY (channel_id);


--
-- Name: crawl_logs crawl_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.crawl_logs
    ADD CONSTRAINT crawl_logs_pkey PRIMARY KEY (log_id);


--
-- Name: event_history event_history_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.event_history
    ADD CONSTRAINT event_history_pkey PRIMARY KEY (history_id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (event_id);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (favorite_id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (setting_id);


--
-- Name: system_settings system_settings_setting_key_key; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_setting_key_key UNIQUE (setting_key);


--
-- Name: favorites uk_favorites_user_event; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT uk_favorites_user_event UNIQUE (user_id, event_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: view_logs view_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.view_logs
    ADD CONSTRAINT view_logs_pkey PRIMARY KEY (log_id);


--
-- Name: idx_channels_code; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_channels_code ON public.channels USING btree (channel_code);


--
-- Name: idx_channels_type; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_channels_type ON public.channels USING btree (channel_type);


--
-- Name: idx_crawl_logs_channel; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_crawl_logs_channel ON public.crawl_logs USING btree (channel_id);


--
-- Name: idx_crawl_logs_started; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_crawl_logs_started ON public.crawl_logs USING btree (started_at DESC);


--
-- Name: idx_crawl_logs_status; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_crawl_logs_status ON public.crawl_logs USING btree (status);


--
-- Name: idx_event_history_date; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_event_history_date ON public.event_history USING btree (changed_at DESC);


--
-- Name: idx_event_history_event; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_event_history_event ON public.event_history USING btree (event_id);


--
-- Name: idx_events_benefit_search; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_benefit_search ON public.events USING gin (benefit_summary public.gin_trgm_ops);


--
-- Name: idx_events_channel; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_channel ON public.events USING btree (channel_id);


--
-- Name: idx_events_created; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_created ON public.events USING btree (created_at DESC);


--
-- Name: idx_events_dates; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_dates ON public.events USING btree (start_date, end_date);


--
-- Name: idx_events_external; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_external ON public.events USING btree (channel_id, external_id);


--
-- Name: idx_events_status; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_status ON public.events USING btree (status);


--
-- Name: idx_events_tags; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_tags ON public.events USING gin (tags);


--
-- Name: idx_events_title_search; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_events_title_search ON public.events USING gin (title public.gin_trgm_ops);


--
-- Name: idx_favorites_created; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_favorites_created ON public.favorites USING btree (created_at DESC);


--
-- Name: idx_favorites_event; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_favorites_event ON public.favorites USING btree (event_id);


--
-- Name: idx_favorites_user; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_favorites_user ON public.favorites USING btree (user_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_role; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_users_role ON public.users USING btree (role);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: idx_view_logs_date; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_view_logs_date ON public.view_logs USING btree (viewed_at DESC);


--
-- Name: idx_view_logs_event; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_view_logs_event ON public.view_logs USING btree (event_id);


--
-- Name: idx_view_logs_user; Type: INDEX; Schema: public; Owner: cs_user
--

CREATE INDEX idx_view_logs_user ON public.view_logs USING btree (user_id);


--
-- Name: channels trigger_channels_updated_at; Type: TRIGGER; Schema: public; Owner: cs_user
--

CREATE TRIGGER trigger_channels_updated_at BEFORE UPDATE ON public.channels FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: events trigger_event_history; Type: TRIGGER; Schema: public; Owner: cs_user
--

CREATE TRIGGER trigger_event_history AFTER INSERT OR DELETE OR UPDATE ON public.events FOR EACH ROW EXECUTE FUNCTION public.log_event_changes();


--
-- Name: events trigger_event_status; Type: TRIGGER; Schema: public; Owner: cs_user
--

CREATE TRIGGER trigger_event_status BEFORE INSERT OR UPDATE ON public.events FOR EACH ROW EXECUTE FUNCTION public.update_event_status();


--
-- Name: events trigger_events_updated_at; Type: TRIGGER; Schema: public; Owner: cs_user
--

CREATE TRIGGER trigger_events_updated_at BEFORE UPDATE ON public.events FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: favorites trigger_favorite_count; Type: TRIGGER; Schema: public; Owner: cs_user
--

CREATE TRIGGER trigger_favorite_count AFTER INSERT OR DELETE ON public.favorites FOR EACH ROW EXECUTE FUNCTION public.update_favorite_count();


--
-- Name: users trigger_users_updated_at; Type: TRIGGER; Schema: public; Owner: cs_user
--

CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: crawl_logs crawl_logs_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.crawl_logs
    ADD CONSTRAINT crawl_logs_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.channels(channel_id) ON DELETE CASCADE;


--
-- Name: event_history event_history_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.event_history
    ADD CONSTRAINT event_history_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id) ON DELETE CASCADE;


--
-- Name: events events_channel_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.channels(channel_id) ON DELETE CASCADE;


--
-- Name: favorites favorites_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id) ON DELETE CASCADE;


--
-- Name: favorites favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: view_logs view_logs_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.view_logs
    ADD CONSTRAINT view_logs_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id) ON DELETE CASCADE;


--
-- Name: view_logs view_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cs_user
--

ALTER TABLE ONLY public.view_logs
    ADD CONSTRAINT view_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict YJWIEiB9YdJqwhVGQDRNnXGACWrsg2uYIujzTMj16coBhumeGvcMBkCuv1CeSEP

