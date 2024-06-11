--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: user_code; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_code (
    user_code_id bigint NOT NULL,
    user_id bigint NOT NULL,
    code character(4) NOT NULL,
    date_start_validity timestamp with time zone
);


ALTER TABLE public.user_code OWNER TO postgres;

--
-- Name: user_code_user_code_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_code_user_code_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_code_user_code_id_seq OWNER TO postgres;

--
-- Name: user_code_user_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_code_user_code_id_seq OWNED BY public.user_code.user_code_id;


--
-- Name: user_code_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_code_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_code_user_id_seq OWNER TO postgres;

--
-- Name: user_code_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_code_user_id_seq OWNED BY public.user_code.user_id;


--
-- Name: user_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_data (
    user_id bigint NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    date_creation timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    activated boolean DEFAULT false NOT NULL
);


ALTER TABLE public.user_data OWNER TO postgres;

--
-- Name: user_data_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_data_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_data_user_id_seq OWNER TO postgres;

--
-- Name: user_data_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_data_user_id_seq OWNED BY public.user_data.user_id;


--
-- Name: user_code user_code_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_code ALTER COLUMN user_code_id SET DEFAULT nextval('public.user_code_user_code_id_seq'::regclass);


--
-- Name: user_code user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_code ALTER COLUMN user_id SET DEFAULT nextval('public.user_code_user_id_seq'::regclass);


--
-- Name: user_data user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data ALTER COLUMN user_id SET DEFAULT nextval('public.user_data_user_id_seq'::regclass);


--
-- Name: user_code user_code_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_code
    ADD CONSTRAINT user_code_pk PRIMARY KEY (user_code_id);


--
-- Name: user_data user_data_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_data
    ADD CONSTRAINT user_data_pk PRIMARY KEY (user_id);


--
-- Name: user_code user_code_user_data_user_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_code
    ADD CONSTRAINT user_code_user_data_user_id_fk FOREIGN KEY (user_id) REFERENCES public.user_data(user_id);


--
-- PostgreSQL database dump complete
--

