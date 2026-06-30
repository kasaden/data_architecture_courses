-- Schéma SQL adapté aux fichiers CSV fournis
-- doctors → patients → consultations(MongoDB) ← prescriptions → medications

CREATE TABLE IF NOT EXISTS doctors (
    id         VARCHAR(10)  PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name  VARCHAR(100) NOT NULL,
    specialty  VARCHAR(150) NOT NULL,
    hospital   VARCHAR(200),
    phone      VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS patients (
    id          VARCHAR(10)  PRIMARY KEY,
    first_name  VARCHAR(100) NOT NULL,
    last_name   VARCHAR(100) NOT NULL,
    dob         DATE         NOT NULL,
    gender      CHAR(1),
    blood_type  VARCHAR(5),
    doctor_id   VARCHAR(10)  REFERENCES doctors(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS medications (
    id       VARCHAR(10)  PRIMARY KEY,
    name     VARCHAR(150) NOT NULL,
    dosage   VARCHAR(50),
    unit     VARCHAR(50),
    category VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS prescriptions (
    id              VARCHAR(10)  PRIMARY KEY,
    consultation_id VARCHAR(20)  NOT NULL,  -- référence applicative vers MongoDB
    medication_id   VARCHAR(10)  REFERENCES medications(id) ON DELETE RESTRICT,
    date            DATE         NOT NULL,
    duration_days   INT          CHECK (duration_days > 0)
);

-- Index pour les jointures fréquentes
CREATE INDEX IF NOT EXISTS idx_patients_doctor       ON patients(doctor_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_consult ON prescriptions(consultation_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_med     ON prescriptions(medication_id);
