CREATE SCHEMA {schema};

CREATE TABLE {schema}.gene (
    gene_id serial not null,
    last_modif date,
    gene_name varchar(50),
    mutant_name varchar(50),
    ensembl_id varchar(255),
    author_initials varchar(50),
    maintainer_initials varchar(50),
    terminated boolean default FALSE,
    date_insert date default CURRENT_DATE,
    note text,
    interest boolean default TRUE,
    injected boolean,
    f1_embryo boolean,
    f1_hetero boolean,
    f2_homo boolean,
    phenotype_zygotic varchar(255),
    phenotype_mz varchar(255),
    target_strategy varchar(50),
    edit_enzyme varchar(50),
    grna_seq_tested text,
    grna_seq_working text,
    target_seq text,
    template_oligo text,
    template_plasmid varchar(255),
    oligo_f0_fw text,
    oligo_f0_rv text,
    genomic_wt_seq text,
    zfin_ref varchar(50),
    PRIMARY KEY (gene_id));

CREATE OR REPLACE FUNCTION {schema}.update_last_modif()
RETURNS TRIGGER 
AS 
$$
BEGIN
    NEW.last_modif = CURRENT_DATE; 
    RETURN NEW;
END;
$$ 
language 'plpgsql';

CREATE TRIGGER last_modif_on_gene_trigger
BEFORE UPDATE
ON {schema}.gene
FOR EACH ROW 
EXECUTE PROCEDURE {schema}.update_last_modif();

CREATE TABLE {schema}.allele (
    allele_id serial not null,
    gene_id integer not null,
    name varchar(50),
    seq text,
    genotyping_oligo text,
    genotyping_strategy text,
    commercial boolean,
    terminated boolean,
    PRIMARY KEY (allele_id));

CREATE TABLE {schema}.option (
    option_id serial not null,
    group_name varchar(50) not null,
    option varchar(50) not null,
    UNIQUE (group_name, option),
    PRIMARY KEY (option_id));

GRANT USAGE ON SCHEMA {schema} TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.gene TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.gene_gene_id_seq TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.allele TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.allele_allele_id_seq TO lab;
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE {schema}.option TO lab;
GRANT SELECT,UPDATE ON TABLE {schema}.option_option_id_seq TO lab;
