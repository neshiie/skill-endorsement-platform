
-- users table
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id         INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            ENUM('student', 'instructor', 'admin') DEFAULT 'student',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- skills table
DROP TABLE IF EXISTS skills;

CREATE TABLE skills (
    skill_id      INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    category      VARCHAR(100),
    description   TEXT,
    UNIQUE KEY unique_skill_name (name)
);

-- endorsements cross-ref table
DROP TABLE IF EXISTS endorsements_xref;

CREATE TABLE endorsements_xref (
    endorsement_id INT AUTO_INCREMENT PRIMARY KEY,
    endorser_id    INT NOT NULL,
    endorsee_id    INT NOT NULL,
    skill_id       INT NOT NULL,
    comment        VARCHAR(255),
    rating         TINYINT UNSIGNED,   
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_endorsements_endorser
        FOREIGN KEY (endorser_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_endorsements_endorsee
        FOREIGN KEY (endorsee_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_endorsements_skill
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        ON DELETE CASCADE,
    CONSTRAINT uc_endorsement_unique
        UNIQUE (endorser_id, endorsee_id, skill_id)
);

-- user_skills cross-ref table (self-claimed)
DROP TABLE IF EXISTS user_skills_xref;

CREATE TABLE user_skills_xref (
    user_skill_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT NOT NULL,
    skill_id            INT NOT NULL,
    level               ENUM('beginner','intermediate','advanced','expert'),
    years_experience    DECIMAL(4,1),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_skills_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_user_skills_skill
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        ON DELETE CASCADE,
    CONSTRAINT uc_user_skill_unique
        UNIQUE (user_id, skill_id)
);


