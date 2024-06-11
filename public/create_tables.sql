DROP TABLE IF EXISTS tagesstatistik;
CREATE TABLE IF NOT EXISTS tagesstatistik
SELECT tc.day, tc.amount, tc.average_delay, tc.max_delay, temp.cancelled_trains, temp.all_trains, temp.probability_of_cancellation
FROM (SELECT CAST(planned_departure AS DATE) AS day,
    COUNT(*) AS amount, 
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, planned_departure, current_departure)),2) AS average_delay, 
    MAX(TIMESTAMPDIFF(MINUTE, planned_departure, current_departure)) AS max_delay FROM trains_copy GROUP BY CAST(planned_departure AS DATE)) AS tc
LEFT JOIN 
(SELECT a.day, a.cancelled_trains, b.all_trains, ROUND((a.cancelled_trains/b.all_trains)*100,2) AS probability_of_cancellation
FROM
(SELECT COUNT(*) AS cancelled_trains, CAST(planned_departure AS DATE) AS day FROM trains_copy WHERE current_departure IS NULL GROUP BY CAST(planned_departure AS DATE)) AS a
LEFT JOIN (SELECT COUNT(*) AS all_trains, CAST(planned_departure AS DATE) AS day FROM trains_copy GROUP BY CAST(planned_departure AS DATE)) AS b
ON a.day=b.day) AS temp
ON tc.day=temp.day;
/*Check daily average delay values*/


/*DROP TABLE IF EXISTS ausfallwahrscheinlichkeit_tage;
CREATE TABLE IF NOT EXISTS ausfallwahrscheinlichkeit_tage AS
SELECT a.day, a.cancelled_trains, b.all_trains, (a.cancelled_trains/b.all_trains)*100 AS probability_of_cancellation
FROM
(SELECT COUNT(*) AS cancelled_trains, CAST(planned_departure AS DATE) AS day FROM trains_copy WHERE current_departure IS NULL GROUP BY CAST(planned_departure AS DATE)) AS a
LEFT JOIN (SELECT COUNT(*) AS all_trains, CAST(planned_departure AS DATE) AS day FROM trains_copy GROUP BY CAST(planned_departure AS DATE)) AS b
ON a.day=b.day;

DROP TABLE IF EXISTS tagesstatistik_unvollständig;
CREATE TABLE IF NOT EXISTS tagesstatistik_unvollständig AS
SELECT 
    CAST(planned_departure AS DATE) AS day,
    COUNT(*) AS amount, 
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, planned_departure, current_departure)),2) AS average_delay, 
    MAX(TIMESTAMPDIFF(MINUTE, planned_departure, current_departure)) AS max_delay 
FROM trains_copy as tc
GROUP BY CAST(planned_departure AS DATE);

DROP TABLE IF EXISTS tagesstatistik;
CREATE TABLE IF NOT EXISTS tagesstatistik
SELECT tu.day, tu.amount, tu.average_delay, tu.max_delay, at.probability_of_cancellation, at.all_trains, at.cancelled_trains
FROM tagesstatistik_unvollständig tu
LEFT JOIN ausfallwahrscheinlichkeit_tage at
ON tu.day = at.day;
*/