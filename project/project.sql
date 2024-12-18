-- --------------------------------------------------------

-- Table structure for table `airline`
CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL,
  PRIMARY KEY (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `airline_staff`
CREATE TABLE `airline_staff` (
  `email` varchar(50) NOT NULL,  -- Username
  `password` varchar(200) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `admin` BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (`email`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `permission`
CREATE TABLE `permission` (
  `email` varchar(50) NOT NULL,
  `permission_type` varchar(50) NOT NULL,
  PRIMARY KEY (`email`, `permission_type`),
  FOREIGN KEY (`email`) REFERENCES `airline_staff` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `airplane`
CREATE TABLE `airplane` (
  `airline_name` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  `seats` int(11) NOT NULL,
  PRIMARY KEY (`airline_name`, `airplane_id`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `airport`
CREATE TABLE `airport` (
  `airport_name` varchar(50) NOT NULL,
  `airport_city` varchar(50) NOT NULL,
  PRIMARY KEY (`airport_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `booking_agent`
CREATE TABLE `booking_agent` (
  `email` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `booking_agent_id` int(11) NOT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `booking_agent_work_for` (
  `email` varchar(50) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  PRIMARY KEY (`email`, `airline_name`),
  FOREIGN KEY (`email`) REFERENCES `booking_agent` (`email`),
  FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `customer`
CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `building_number` varchar(30) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` varchar(13) NOT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  PRIMARY KEY (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `flight`
CREATE TABLE `flight` (
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(50) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(50) NOT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `status` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  PRIMARY KEY (`airline_name`, `flight_num`),
  FOREIGN KEY (`airline_name`, `airplane_id`) REFERENCES `airplane` (`airline_name`, `airplane_id`),
  FOREIGN KEY (`departure_airport`) REFERENCES `airport` (`airport_name`),
  FOREIGN KEY (`arrival_airport`) REFERENCES `airport` (`airport_name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `ticket`
CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  PRIMARY KEY (`ticket_id`),
  FOREIGN KEY (`airline_name`, `flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

-- Table structure for table `purchases`
CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(50), -- For passengers using booking_agents there are no need
  `booking_agent_id` int(10),
  `purchase_date` date NOT NULL,
  `phone_number` varchar(13) NOT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  PRIMARY KEY (`ticket_id`, `passport_number`), 
  FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
