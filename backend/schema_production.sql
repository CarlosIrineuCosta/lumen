--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

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
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: cities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cities (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    country character varying(100) NOT NULL,
    region character varying(100),
    latitude numeric(10,8),
    longitude numeric(11,8),
    population integer,
    is_capital boolean DEFAULT false,
    tier integer DEFAULT 1,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: cities_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cities_id_seq OWNED BY public.cities.id;


--
-- Name: photo_collaborators; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.photo_collaborators (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    photo_id uuid,
    user_id character varying(128),
    display_name character varying(100) NOT NULL,
    handle character varying(50),
    role character varying(50),
    role_data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: photo_interactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.photo_interactions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    photo_id uuid,
    user_id character varying(128),
    interaction_type character varying(20) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: photos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.photos (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id character varying(128),
    title character varying(200),
    description text,
    image_url character varying(500) NOT NULL,
    thumbnail_url character varying(500),
    city_id integer,
    location_name character varying(200),
    camera_data jsonb,
    ai_tags jsonb,
    user_tags text[],
    content_rating character varying(20) DEFAULT 'general'::character varying,
    category character varying(50) DEFAULT 'portrait'::character varying,
    series_id uuid,
    is_deleted boolean DEFAULT false,
    is_collaborative boolean DEFAULT false,
    model_release_status character varying(20) DEFAULT 'none'::character varying,
    extra_metadata jsonb DEFAULT '{}'::jsonb,
    is_public boolean DEFAULT true,
    view_count integer DEFAULT 0,
    is_portfolio boolean DEFAULT false,
    status character varying(20) DEFAULT 'active'::character varying,
    upload_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE photos; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.photos IS 'Photos table with UUID primary keys, referencing Firebase UID for users';


--
-- Name: COLUMN photos.user_id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.photos.user_id IS 'References users.id (Firebase UID) for proper OAuth ID path mapping';


--
-- Name: series; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.series (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id character varying(128) NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    cover_photo_id uuid,
    photo_count integer DEFAULT 0,
    is_public boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE series; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.series IS 'Photo series/collections owned by users';

CREATE INDEX idx_series_user_id ON public.series USING btree (user_id);
CREATE INDEX idx_photos_series_id ON public.photos USING btree (series_id);


--
-- Name: specialties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.specialties (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    description text,
    applicable_to text[] DEFAULT ARRAY['photographer'::text, 'model'::text],
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: specialties_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.specialties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: specialties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.specialties_id_seq OWNED BY public.specialties.id;


--
-- Name: user_connections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_connections (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    requester_id character varying(128),
    target_id character varying(128),
    status character varying(20) DEFAULT 'pending'::character varying,
    message text,
    connection_data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_specialties; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_specialties (
    user_id character varying(128) NOT NULL,
    specialty_id integer NOT NULL,
    is_primary boolean DEFAULT false,
    experience_level character varying(20) DEFAULT 'intermediate'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_types (
    id integer NOT NULL,
    type_name character varying(20) NOT NULL,
    display_name character varying(50),
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: user_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_types_id_seq OWNED BY public.user_types.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id character varying(128) NOT NULL,
    email character varying(255) NOT NULL,
    handle character varying(50) NOT NULL,
    display_name character varying(100) NOT NULL,
    city_id integer,
    primary_user_type integer,
    birth_date date NOT NULL,
    country_code character varying(3) NOT NULL,
    tos_accepted_at timestamp with time zone NOT NULL,
    gender character varying(20),
    age integer,
    height_cm integer,
    weight_kg integer,
    ethnicity character varying(50),
    eye_color character varying(30),
    hair_color character varying(30),
    measurements jsonb,
    has_tattoos boolean DEFAULT false,
    has_piercings boolean DEFAULT false,
    profile_image_url character varying(500),
    bio text,
    website character varying(500),
    profile_data jsonb DEFAULT '{}'::jsonb,
    availability_data jsonb DEFAULT '{}'::jsonb,
    privacy_settings jsonb DEFAULT '{"show_age": true, "show_city": false, "show_country": true}'::jsonb,
    stripe_customer_id character varying(255),
    stripe_subscription_id character varying(255),
    subscription_tier character varying(50) DEFAULT 'free'::character varying,
    subscription_status character varying(50) DEFAULT 'active'::character varying,
    subscription_data jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_active timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public.users IS 'Users table with Firebase UID as primary key for OAuth compatibility';


--
-- Name: COLUMN users.id; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.users.id IS 'Firebase UID (28-char alphanumeric string) - primary key for OAuth integration';

COMMENT ON COLUMN public.users.birth_date IS 'User birth date for age verification';
COMMENT ON COLUMN public.users.country_code IS 'ISO country code for legal age validation';
COMMENT ON COLUMN public.users.tos_accepted_at IS 'Timestamp when user accepted Terms of Service';
COMMENT ON COLUMN public.users.subscription_tier IS 'Current subscription tier (free, hobbyist, professional, etc.)';
COMMENT ON COLUMN public.users.subscription_status IS 'Subscription status (active, canceled, past_due, etc.)';

CREATE INDEX idx_users_country_code ON public.users USING btree (country_code);
CREATE INDEX idx_users_birth_date ON public.users USING btree (birth_date);


--
-- Name: cities id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cities ALTER COLUMN id SET DEFAULT nextval('public.cities_id_seq'::regclass);


--
-- Name: specialties id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.specialties ALTER COLUMN id SET DEFAULT nextval('public.specialties_id_seq'::regclass);


--
-- Name: user_types id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_types ALTER COLUMN id SET DEFAULT nextval('public.user_types_id_seq'::regclass);


--
-- Name: cities cities_name_country_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_name_country_key UNIQUE (name, country);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (id);


--
-- Name: photo_collaborators photo_collaborators_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_collaborators
    ADD CONSTRAINT photo_collaborators_pkey PRIMARY KEY (id);


--
-- Name: photo_interactions photo_interactions_photo_id_user_id_interaction_type_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_interactions
    ADD CONSTRAINT photo_interactions_photo_id_user_id_interaction_type_key UNIQUE (photo_id, user_id, interaction_type);


--
-- Name: photo_interactions photo_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_interactions
    ADD CONSTRAINT photo_interactions_pkey PRIMARY KEY (id);


--
-- Name: photos photos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_pkey PRIMARY KEY (id);


--
-- Name: series series_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_pkey PRIMARY KEY (id);


--
-- Name: specialties specialties_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.specialties
    ADD CONSTRAINT specialties_name_key UNIQUE (name);


--
-- Name: specialties specialties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.specialties
    ADD CONSTRAINT specialties_pkey PRIMARY KEY (id);


--
-- Name: user_connections user_connections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_connections
    ADD CONSTRAINT user_connections_pkey PRIMARY KEY (id);


--
-- Name: user_connections user_connections_requester_id_target_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_connections
    ADD CONSTRAINT user_connections_requester_id_target_id_key UNIQUE (requester_id, target_id);


--
-- Name: user_specialties user_specialties_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_specialties
    ADD CONSTRAINT user_specialties_pkey PRIMARY KEY (user_id, specialty_id);


--
-- Name: user_types user_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_types
    ADD CONSTRAINT user_types_pkey PRIMARY KEY (id);


--
-- Name: user_types user_types_type_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_types
    ADD CONSTRAINT user_types_type_name_key UNIQUE (type_name);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_handle_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_handle_key UNIQUE (handle);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_cities_location; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cities_location ON public.cities USING gist (point((longitude)::double precision, (latitude)::double precision));


--
-- Name: idx_photo_collaborators_photo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photo_collaborators_photo ON public.photo_collaborators USING btree (photo_id);


--
-- Name: idx_photo_collaborators_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photo_collaborators_user ON public.photo_collaborators USING btree (user_id);


--
-- Name: idx_photo_interactions_photo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photo_interactions_photo ON public.photo_interactions USING btree (photo_id);


--
-- Name: idx_photo_interactions_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photo_interactions_user ON public.photo_interactions USING btree (user_id);


--
-- Name: idx_photos_ai_tags; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_ai_tags ON public.photos USING gin (ai_tags);


--
-- Name: idx_photos_city; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_city ON public.photos USING btree (city_id);


--
-- Name: idx_photos_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_created ON public.photos USING btree (created_at DESC);


--
-- Name: idx_photos_metadata; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_metadata ON public.photos USING gin (extra_metadata);


--
-- Name: idx_photos_portfolio; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_portfolio ON public.photos USING btree (is_portfolio) WHERE (is_portfolio = true);


--
-- Name: idx_photos_public; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_public ON public.photos USING btree (is_public) WHERE (is_public = true);


--
-- Name: idx_photos_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_photos_user ON public.photos USING btree (user_id);


--
-- Name: idx_user_connections_requester; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_connections_requester ON public.user_connections USING btree (requester_id);


--
-- Name: idx_user_connections_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_connections_target ON public.user_connections USING btree (target_id);


--
-- Name: idx_user_specialties_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_specialties_user ON public.user_specialties USING btree (user_id);


--
-- Name: idx_users_city; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_city ON public.users USING btree (city_id);


--
-- Name: idx_users_handle; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_handle ON public.users USING btree (handle);


--
-- Name: idx_users_privacy; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_privacy ON public.users USING gin (privacy_settings);


--
-- Name: idx_users_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_users_type ON public.users USING btree (primary_user_type);


--
-- Name: user_connections update_connections_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_connections_updated_at BEFORE UPDATE ON public.user_connections FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: photos update_photos_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_photos_updated_at BEFORE UPDATE ON public.photos FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: photo_collaborators photo_collaborators_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_collaborators
    ADD CONSTRAINT photo_collaborators_photo_id_fkey FOREIGN KEY (photo_id) REFERENCES public.photos(id) ON DELETE CASCADE;


--
-- Name: photo_collaborators photo_collaborators_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_collaborators
    ADD CONSTRAINT photo_collaborators_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: photo_interactions photo_interactions_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_interactions
    ADD CONSTRAINT photo_interactions_photo_id_fkey FOREIGN KEY (photo_id) REFERENCES public.photos(id) ON DELETE CASCADE;


--
-- Name: photo_interactions photo_interactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photo_interactions
    ADD CONSTRAINT photo_interactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: photos photos_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id);


--
-- Name: photos photos_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: photos_series_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_series_id_fkey FOREIGN KEY (series_id) REFERENCES public.series(id) ON DELETE SET NULL;


--
-- Name: series_cover_photo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_cover_photo_id_fkey FOREIGN KEY (cover_photo_id) REFERENCES public.photos(id) ON DELETE SET NULL;


--
-- Name: series_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.series
    ADD CONSTRAINT series_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_connections user_connections_requester_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_connections
    ADD CONSTRAINT user_connections_requester_id_fkey FOREIGN KEY (requester_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_connections user_connections_target_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_connections
    ADD CONSTRAINT user_connections_target_id_fkey FOREIGN KEY (target_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_specialties user_specialties_specialty_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_specialties
    ADD CONSTRAINT user_specialties_specialty_id_fkey FOREIGN KEY (specialty_id) REFERENCES public.specialties(id);


--
-- Name: user_specialties user_specialties_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_specialties
    ADD CONSTRAINT user_specialties_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id);


--
-- Name: users users_primary_user_type_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_primary_user_type_fkey FOREIGN KEY (primary_user_type) REFERENCES public.user_types(id);


--
-- PostgreSQL database dump complete
--
