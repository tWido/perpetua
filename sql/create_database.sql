CREATE TABLE `reviews` (
  `id` int(11) NOT NULL,
  `school_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `time_attended` tinyint(4) DEFAULT NULL,
  `completed` tinyint(4) NOT NULL,
  `pros` text DEFAULT NULL,
  `cons` text DEFAULT NULL,
  `rating_teachers` tinyint(4) DEFAULT NULL,
  `rating_peers` tinyint(4) DEFAULT NULL,
  `rating_dorms` tinyint(4) DEFAULT NULL,
  `rating_food` tinyint(4) DEFAULT NULL,
  `rating_subjects` tinyint(4) DEFAULT NULL,
  `rating_building` tinyint(4) DEFAULT NULL,
  `rating_options` tinyint(4) DEFAULT NULL,
  `rating_activities` tinyint(4) DEFAULT NULL,
  `token_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_reviews_schools_idx` (`school_id`),
  KEY `fk_reviews_students_idx` (`student_id`),
  KEY `fk_reviews_tokens_idx` (`token_id`),
  CONSTRAINT `fk_reviews_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_reviews_students` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_reviews_tokens` FOREIGN KEY (`token_id`) REFERENCES `tokens` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);


CREATE TABLE `school_info` (
  `id` int(11) NOT NULL,
  `school_id` int(11) NOT NULL,
  `kitchen` varchar(45) DEFAULT NULL,
  `stipendium` varchar(45) DEFAULT NULL,
  `art_activities` varchar(127) DEFAULT NULL,
  `sport_activities` varchar(127) DEFAULT NULL,
  `other_activities` varchar(127) DEFAULT NULL,
  `indoor_gym` varchar(127) DEFAULT NULL,
  `playground` varchar(127) DEFAULT NULL,
  `notes` varchar(127) DEFAULT NULL,
  `homepage` varchar(127) DEFAULT NULL,
  `students` int(11) DEFAULT NULL,
  `class_count` int(11) DEFAULT NULL,
  `foreign_languages` varchar(127) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `school_id_UNIQUE` (`school_id`),
  CONSTRAINT `fk_school_info_1` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);

CREATE TABLE `schools` (
  `id` int(11) NOT NULL,
  `name` varchar(127) NOT NULL,
  `region` varchar(45) NOT NULL,
  `town` varchar(127) NOT NULL,
  `latitude` decimal(11,8) NOT NULL,
  `longitude` decimal(11,8) NOT NULL,
  `language` varchar(45) NOT NULL,
  `level` enum('ELEMENTARY','HIGHSCHOOL','GYMNASIUM','COLLEGE') NOT NULL,
  `type` enum('STATE','PRIVATE','RELIGIOUS') NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `students` (
  `id` int(11) NOT NULL,
  `nick` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `tokens` (
  `id` int(11) NOT NULL,
  `school_id` int(11) DEFAULT NULL,
  `uses` tinyint(4) DEFAULT NULL,
  `valid_till` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_tokens_schools_idx` (`school_id`),
  CONSTRAINT `fk_tokens_schools` FOREIGN KEY (`school_id`) REFERENCES `schools` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);
