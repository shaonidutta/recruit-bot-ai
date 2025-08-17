const fetchJobs = require('../../utils/fetchHelper');
const { JOB_SOURCES } = require('../../config/constants');

module.exports = function (keywords) {
    return fetchJobs(JOB_SOURCES.INDEED, keywords);
};
