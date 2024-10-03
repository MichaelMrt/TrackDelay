DROP TABLE IF EXISTS tagesstatistik;
CREATE TABLE IF NOT EXISTS tagesstatistik
SELECT tc.day, tc.amount, tc.average_delay, tc.max_delay, temp.cancelled_trains, temp.all_trains, temp.probability_of_cancellation
FROM (SELECT CAST(planned_departure AS DATE) AS day,
    COUNT(*) AS amount, 
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, planned_departure, current_departure)),2) AS average_delay, 
    MAX(TIMESTAMPDIFF(MINUTE, planned_departure, current_departure)) AS max_delay FROM trains GROUP BY CAST(planned_departure AS DATE)) AS tc
LEFT JOIN 
(SELECT a.day, a.cancelled_trains, b.all_trains, ROUND((a.cancelled_trains/b.all_trains)*100,2) AS probability_of_cancellation
FROM
(SELECT COUNT(*) AS cancelled_trains, CAST(planned_departure AS DATE) AS day FROM trains WHERE current_departure IS NULL GROUP BY CAST(planned_departure AS DATE)) AS a
LEFT JOIN (SELECT COUNT(*) AS all_trains, CAST(planned_departure AS DATE) AS day FROM trains GROUP BY CAST(planned_departure AS DATE)) AS b
ON a.day=b.day) AS temp
ON tc.day=temp.day;