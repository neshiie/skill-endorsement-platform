INSERT INTO users (username, email, hashed_password, full_name, role)
VALUES
('alice', 'alice@example.com', 'hashed_pw_here', 'Alice Smith', 'student'),
('bob', 'bob@example.com', 'hashed_pw_here', 'Bob Johnson', 'student'),
('prof_jones', 'jones@example.com', 'hashed_pw_here', 'Prof. Jones', 'instructor');

INSERT INTO skills (name, category, description)
VALUES
('Python', 'Programming', 'General-purpose programming language'),
('MySQL', 'Databases', 'Relational database management'),
('Git', 'Tools', 'Version control system');

INSERT INTO user_skills_xref (user_id, skill_id, level, years_experience)
VALUES
(1, 1, 'advanced', 3.0), -- Alice, Python
(1, 3, 'intermediate', 2.0), -- Alice, Git
(2, 1, 'intermediate', 1.5), -- Bob, Python
(2, 2, 'beginner', 0.5); -- Bob, MySQL

INSERT INTO endorsements_xref (endorser_id, endorsee_id, skill_id, comment, rating)
VALUES
(3, 1, 1, 'Excellent Python developer', 5),  -- Prof endorses Alice for Python
(3, 2, 1, 'Good understanding of fundamentals', 4),
(1, 2, 3, 'Bob is reliable with Git', 4);
