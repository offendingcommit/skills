const fs = require('fs');
const path = require('path');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function loadProfileScheduleFiles(workspaceRoot, profileId) {
  const base = path.join(workspaceRoot, 'schedules', 'profiles', profileId);
  const weeklyPath = path.join(base, 'weekly.json');
  const specialPath = path.join(base, 'special_events.json');
  const termPath = path.join(base, 'term_calendar.json');

  const weekly = fs.existsSync(weeklyPath) ? readJson(weeklyPath) : null;
  const special = fs.existsSync(specialPath) ? readJson(specialPath) : null;
  const term = fs.existsSync(termPath) ? readJson(termPath) : null;

  return { weekly, special, term, paths: { weeklyPath, specialPath, termPath } };
}

module.exports = { loadProfileScheduleFiles };
