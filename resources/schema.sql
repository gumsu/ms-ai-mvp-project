CREATE table employee (
    id int(11) NOT NULL AUTO_INCREMENT,
    name varchar(255) NOT NULL,
    residence_city varchar(255) NOT NULL,
    department varchar(255) NOT NULL,
    created_at varchar(255) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

create Table employee_history (
    id int(11) NOT NULL AUTO_INCREMENT,
    employee_id int(11) NOT NULL,
    project_name varchar(255) NOT NULL,
    project_role varchar(255) NOT NULL,
    start_date varchar(255) NOT NULL,
    end_date varchar(255) NOT NULL,
    tech_stack varchar(255) NOT NULL,
    region_city varchar(255) NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (employee_id) REFERENCES employee(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
