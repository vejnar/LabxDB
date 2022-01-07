CREATE SCHEMA IF NOT EXISTS {schema};

CREATE TABLE {schema}.project (
    project_id serial not null,
    project_ref varchar(50),
    project_name varchar(100),
    label_short varchar(100),
    label_long varchar(255),
    scientist varchar(255),
    external_scientist varchar(255),
    sra_ref varchar(50),
    UNIQUE (project_ref),
    PRIMARY KEY (project_id));

CREATE TABLE {schema}.sample (
    sample_id serial not null,
    sample_ref varchar(50),
    project_ref varchar(50),
    label_short varchar(100),
    label_long varchar(255),
    species varchar(10),
    strain_maternal varchar(50),
    strain_paternal varchar(50),
    genotype varchar(50),
    ploidy varchar(50),
    age_hpf real,
    stage varchar(50),
    tissue varchar(50),
    condition varchar(50),
    treatment varchar(255),
    selection varchar(50),
    molecule varchar(50),
    library_protocol varchar(50),
    adapter_5p varchar(50),
    adapter_3p varchar(50),
    track_priority integer,
    track_color varchar(50),
    sra_ref varchar(255),
    notes varchar(255),
    UNIQUE (sample_ref),
    PRIMARY KEY (sample_id));

CREATE TABLE {schema}.replicate (
    replicate_id serial not null,
    replicate_ref varchar(50),
    replicate_order integer,
    sample_ref varchar(50),
    label_short varchar(100),
    label_long varchar(255),
    sra_ref varchar(255),
    publication_ref varchar(50),
    notes varchar(255),
    UNIQUE (replicate_ref),
    PRIMARY KEY (replicate_id));

CREATE TABLE {schema}.run (
    run_id serial not null,
    run_ref varchar(50),
    run_order integer,
    replicate_ref varchar(50),
    tube_label varchar(100),
    barcode varchar(50),
    second_barcode varchar(50),
    request_ref varchar(50),
    request_date date,
    failed boolean,
    flowcell varchar(50),
    platform varchar(50),
    quality_scores varchar(50),
    directional boolean,
    paired boolean,
    r1_strand varchar(1),
    spots bigint,
    max_read_length integer,
    sra_ref text,
    notes varchar(255),
    UNIQUE (run_ref),
    PRIMARY KEY (run_id));

CREATE TABLE {schema}.option (
    option_id serial not null,
    group_name varchar(50) not null,
    option varchar(50) not null,
    UNIQUE (group_name, option),
    PRIMARY KEY (option_id));

CREATE TABLE {schema}.publication (
    publication_id serial not null,
    publication_ref varchar(50),
    title varchar(255),
    publication_date date,
    pubmed_id varchar(50),
    sra_ref text,
    UNIQUE (publication_ref),
    PRIMARY KEY (publication_id));

GRANT USAGE ON SCHEMA {schema} TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.project to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.sample to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.replicate to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.run to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.option to lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON {schema}.publication to lab;

GRANT SELECT,UPDATE ON TABLE {schema}.project_project_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.sample_sample_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.replicate_replicate_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.run_run_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.option_option_id_seq TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.publication_publication_id_seq TO lab;
