CREATE TYPE object_type AS ENUM ('DIMENSIONS', 'WALL', 'LOCATION', 'MARKER');

CREATE TABLE objects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type object_type NOT NULL,
    data VARCHAR(255) NOT NULL 
);

INSERT INTO objects (name, type, data) VALUES 
    ('floor', 'DIMENSIONS', '{ "width": 35, "height": 23 }'),
    ('bottom wall', 'WALL', '{ "startX": 9, "endX": 25, "startY": 0, "endY": 0 }'),
    ('middle wall', 'WALL', '{ "startX": 9, "endX": 25, "startY": 11, "endY": 12 }'),
    ('top wall', 'WALL', '{ "startX": 9, "endX": 25, "startY": 23, "endY": 23 }'),
    ('z', 'MARKER', '{ "x": 4, "y": 5 }'),
    ('o', 'MARKER', '{ "x": 31, "y": 5 }'),
    ('s', 'MARKER', '{ "x": 4, "y": 18 }'),
    ('x', 'MARKER', '{ "x": 31, "y": 18 }'),
    ('milk', 'LOCATION', '{ "x": 14, "y": 5 }'),
    ('bread', 'LOCATION', '{ "x": 14, "y": 18 }')
;
