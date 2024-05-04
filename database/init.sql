CREATE TYPE object_type AS ENUM ('DIMENSIONS', 'WALL', 'LOCATION');

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
    ('milk', 'LOCATION', '{ "x": 14, "y": 5 }')
;
