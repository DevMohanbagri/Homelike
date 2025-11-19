-- Sample Test Data for Hostel Maintenance System
-- This file contains sample data for testing the system
-- Run with: mysql -u root -p homelike < test_data.sql

-- Clear existing data (use with caution in production)
SET FOREIGN_KEY_CHECKS=0;
TRUNCATE TABLE Complaint;
TRUNCATE TABLE Student;
TRUNCATE TABLE Warden;
TRUNCATE TABLE Filter;
TRUNCATE TABLE Washroom;
TRUNCATE TABLE Rooms;
TRUNCATE TABLE Hostel;
SET FOREIGN_KEY_CHECKS=1;

-- ==================== HOSTELS ====================
INSERT INTO Hostel (HId, HName, WName) VALUES 
('H1', 'Hostel A (Boys)', 'Hostel A Main Building'),
('H2', 'Hostel B (Girls)', 'Hostel B Main Building'),
('H3', 'Hostel C (Mixed)', 'Hostel C Main Building');

-- ==================== ROOMS ====================
INSERT INTO Rooms (RNo, Occupancy, Block, Floor) VALUES 
-- Hostel A
('R101', 2, 'A', 1),
('R102', 2, 'A', 1),
('R103', 2, 'A', 1),
('R201', 2, 'A', 2),
('R202', 2, 'A', 2),
('R301', 2, 'A', 3),
-- Hostel B
('R104', 3, 'B', 1),
('R105', 3, 'B', 1),
('R203', 3, 'B', 2),
-- Hostel C
('R106', 1, 'C', 1),
('R107', 1, 'C', 1);

-- ==================== WASHROOMS ====================
INSERT INTO Washroom (WashroomID, Floor, Block) VALUES 
('W1', 1, 'A'),
('W2', 2, 'A'),
('W3', 3, 'A'),
('W4', 1, 'B'),
('W5', 2, 'B'),
('W6', 1, 'C');

-- ==================== WATER FILTERS ====================
INSERT INTO Filter (FId, Floor, Block) VALUES 
('F1', 1, 'A'),
('F2', 2, 'A'),
('F3', 3, 'A'),
('F4', 1, 'B'),
('F5', 1, 'C');

-- ==================== WARDENS ====================
INSERT INTO Warden (WardenID, WName, Wmail, Wcontact, HId) VALUES 
('WAR1', 'John Doe', 'warden@university.edu', '+91-9876543210', 'H1'),
('WAR2', 'Sarah Johnson', 'warden2@university.edu', '+91-9876543211', 'H2'),
('WAR3', 'Michael Chen', 'warden3@university.edu', '+91-9876543212', 'H3');

-- ==================== STUDENTS ====================
INSERT INTO Student (SId, SName, Smail, Scontact, HId, RNo) VALUES 
('STU1', 'Jane Smith', 'student@university.edu', '+91-9123456789', 'H1', 'R101'),
('STU2', 'Alice Johnson', 'student2@university.edu', '+91-9123456790', 'H1', 'R102'),
('STU3', 'Bob Wilson', 'student3@university.edu', '+91-9123456791', 'H1', 'R103'),
('STU4', 'Carol White', 'student4@university.edu', '+91-9123456792', 'H1', 'R201'),
('STU5', 'David Brown', 'student5@university.edu', '+91-9123456793', 'H2', 'R104'),
('STU6', 'Emma Davis', 'student6@university.edu', '+91-9123456794', 'H2', 'R105'),
('STU7', 'Frank Miller', 'student7@university.edu', '+91-9123456795', 'H3', 'R106');

-- ==================== COMPLAINTS ====================
INSERT INTO Complaint (CId, description, Status, date_time, SId, WardenID, HId, RNo, WashroomID, FId) VALUES 

-- PENDING COMPLAINTS
('C001', 'Water leakage from ceiling in room', 'Pending', NOW(), 'STU1', 'WAR1', 'H1', 'R101', NULL, NULL),
('C002', 'Broken tap in washroom, water flowing continuously', 'Pending', NOW(), 'STU2', 'WAR1', 'H1', NULL, 'W1', NULL),
('C003', 'Water filter not working properly, low water pressure', 'Pending', DATE_SUB(NOW(), INTERVAL 2 DAY), 'STU3', 'WAR1', 'H1', NULL, NULL, 'F1'),

-- RESOLVED COMPLAINTS (awaiting student confirmation)
('C004', 'Broken window pane in room', 'Resolved', DATE_SUB(NOW(), INTERVAL 3 DAY), 'STU4', 'WAR1', 'H1', 'R201', NULL, NULL),
('C005', 'Damaged floor tiles in washroom', 'Resolved', DATE_SUB(NOW(), INTERVAL 1 DAY), 'STU5', 'WAR2', 'H2', NULL, 'W4', NULL),

-- CONFIRMED COMPLAINTS (resolved and confirmed by student)
('C006', 'Faulty light bulb in washroom', 'Confirmed', DATE_SUB(NOW(), INTERVAL 5 DAY), 'STU6', 'WAR2', 'H2', NULL, 'W5', NULL),
('C007', 'Clogged drain in room', 'Confirmed', DATE_SUB(NOW(), INTERVAL 7 DAY), 'STU1', 'WAR1', 'H1', 'R102', NULL, NULL),
('C008', 'Water filter replaced successfully', 'Confirmed', DATE_SUB(NOW(), INTERVAL 4 DAY), 'STU3', 'WAR1', 'H1', NULL, NULL, 'F2');

-- ==================== STATISTICS ====================
-- Total Complaints: 8
-- Pending: 3
-- Resolved: 2
-- Confirmed: 3

-- Query to verify data
SELECT 'Hostel Data Summary' AS 'Summary';
SELECT COUNT(*) AS Total_Hostels FROM Hostel;
SELECT COUNT(*) AS Total_Rooms FROM Rooms;
SELECT COUNT(*) AS Total_Washrooms FROM Washroom;
SELECT COUNT(*) AS Total_Filters FROM Filter;
SELECT COUNT(*) AS Total_Wardens FROM Warden;
SELECT COUNT(*) AS Total_Students FROM Student;
SELECT COUNT(*) AS Total_Complaints FROM Complaint;

SELECT 'Complaint Status Breakdown' AS 'Status';
SELECT Status, COUNT(*) AS Count FROM Complaint GROUP BY Status;
