UPDATE country
SET country_name = 'Belgique'
WHERE country_name LIKE '%Belgique%';

UPDATE country
SET country_name = 'Suisse'
WHERE country_name LIKE '%Suisse%';

UPDATE country
SET country_name = 'Espagne'
WHERE country_name LIKE '%Esp%';

UPDATE country
SET country_name = 'Italie'
WHERE country_name LIKE '%Ita%';

create temp table temp_import_user (
    numero int,
    prenom varchar(50),
    nom varchar(50),
    date_anniversaire date,
    ville varchar(50),
    rue varchar(50),
    numero_rue INT,
    pays varchar(50),
    code_postal INT
);

COPY temp_import_user
FROM '/data/donnees_fictives_v3_PROPRE.csv'
DELIMITER ','
CSV HEADER;

create temp table temp_import_flight (
    start_time VARCHAR(50),
    pilot int,
    launch varchar(100),
    route char(2),
    lenght DECIMAL(5,2),
    points DECIMAL(5,2),
    airtime TIME,
    glider_class varchar(3)
);
truncate temp_import_flight;
COPY temp_import_flight
FROM '/data/clean_flight.csv'
DELIMITER ','
CSV HEADER;

UPDATE temp_import_flight
SET start_time =(
    to_timestamp(
        regexp_replace(start_time, '\s*=?UTC', '', 'i'),
        'DD.MM.YY HH24:MI')
    );
select * from temp_import_flight;

INSERT INTO street (street_name)
SELECT DISTINCT rue FROM temp_import_user
ON CONFLICT DO NOTHING ;

INSERT INTO city(city_name, city_postal_code)
SELECT DISTINCT ville, code_postal FROM temp_import_user
ON CONFLICT (city_name) DO NOTHING
;

CREATE OR REPLACE FUNCTION insert_user()
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
BEGIN
    INSERT INTO users (users_number, users_firstname, users_lastname, users_email, users_phone, users_birthday)
    SELECT
        tu.numero,
        tu.prenom,
        tu.nom,
        LOWER(tu.prenom || '.' || tu.nom || '@vayora.be') AS users_email,
        CASE
            WHEN lower(tu.pays) = 'france' THEN
                '+33 06 00' || tu.numero::CHAR
            WHEN LOWER(tu.pays) = 'belgique' THEN
                '+32 047000' || tu.numero::CHAR
            END AS users_phone,
        tu.date_anniversaire
        FROM temp_import_user tu;
END;
$$;

select * from temp_import_user;

SELECT * FROM insert_user();

INSERT INTO address (address_street_number, address_city_id, address_street_id, address_country_id)
SELECT
    tu.numero_rue::varchar,
    c.city_id,
    s.street_id,
    ct.country_id
FROM temp_import_user tu
JOIN city c ON c.city_name = tu.ville
JOIN street s ON s.street_name = tu.rue
JOIN country ct ON ct.country_name = tu.pays
ON CONFLICT DO NOTHING;

UPDATE users u
SET users_address_id = ad.address_id
FROM address ad
JOIN city c ON ad.address_city_id = c.city_id
JOIN street s ON ad.address_street_id = s.street_id
JOIN country ct ON ct.country_id = ad.address_country_id
INNER JOIN temp_import_user tu ON c.city_name = tu.ville
AND s.street_name = tu.rue
AND ad.address_street_number = tu.numero_rue::varchar
AND ct.country_name = tu.pays
WHERE u.users_number = tu.numero;

INSERT INTO pilot (pilot_user_ref)
SELECT users_id
FROM users
WHERE users_lastname = 'Do';

INSERT INTO validator (validator_user_ref)
SELECT users_id
FROM users
WHERE users_firstname = 'Mason' OR users_lastname = 'Do';

INSERT INTO flight ("flight_starttime", "flight_airtime", flight_distance, "flight_maxheight", flight_pilot_id, flight_takeoff_id)
SELECT
    tf.start_time::TIMESTAMP WITH TIME ZONE,
    tf.airtime,
    tf.lenght,
    0,
    p.pilot_id,
    tk.takeoff_id
FROM temp_import_flight tf
JOIN users u ON u.users_number = tf.pilot
JOIN pilot p ON p.pilot_user_ref = u.users_id
JOIN takeoff tk ON tk.takeoff_name = tf.launch;

