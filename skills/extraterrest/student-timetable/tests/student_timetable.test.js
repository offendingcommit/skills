const assert = require('assert');
const fs = require('fs');
const path = require('path');

const { loadProfilesRegistry, resolveProfile } = require('../profiles_registry.js');
const { dayScheduleForProfile } = require('../student_timetable_service.js');

function withTempDir(fn) {
  const tmpBase = fs.mkdtempSync(path.join(require('os').tmpdir(), 'student-timetable-'));
  try {
    return fn(tmpBase);
  } finally {
    fs.rmSync(tmpBase, { recursive: true, force: true });
  }
}

function writeJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

(function testProfileResolutionOrderAndAmbiguity() {
  const registry = {
    version: 1,
    dataRoot: 'schedules/profiles',
    profiles: [
      { profile_id: 'kai', type: 'child', display_name: 'Kai', aliases: ['kk'] },
      { profile_id: 'p2', type: 'child', display_name: 'kai', aliases: [] }
    ]
  };

  // exact profile_id wins over display_name
  const r1 = resolveProfile(registry, 'kai', { allowDefaultToSelf: false });
  assert.equal(r1.ok, true);
  assert.equal(r1.profile.profile_id, 'kai');

  // ambiguous: "kai" matches profile_id of first profile; should still resolve
  const r2 = resolveProfile(registry, 'kai ', { allowDefaultToSelf: false });
  assert.equal(r2.ok, true);
})();

(function testGenericAliasForcesClarification() {
  const registry = {
    version: 1,
    dataRoot: 'schedules/profiles',
    profiles: [{ profile_id: 'aidan', type: 'child', display_name: 'Aidan', aliases: ['kid'] }]
  };

  const r = resolveProfile(registry, 'kid', { allowDefaultToSelf: false });
  assert.equal(r.ok, false);
  assert.equal(r.reason, 'generic_alias');
})();

(function testDefaultToSelfOnlyWhenConfigured() {
  const regNoSelf = { version: 1, dataRoot: 'schedules/profiles', profiles: [{ profile_id: 'a', type: 'child', display_name: 'A', aliases: [] }] };
  const r1 = resolveProfile(regNoSelf, null, { allowDefaultToSelf: true });
  assert.equal(r1.ok, false);

  const regSelf = { version: 1, dataRoot: 'schedules/profiles', profiles: [{ profile_id: 'me', type: 'self', display_name: 'Me', aliases: [] }] };
  const r2 = resolveProfile(regSelf, null, { allowDefaultToSelf: true });
  assert.equal(r2.ok, true);
  assert.equal(r2.profile.type, 'self');
})();

(function testDayScheduleWeeklyPlusSpecialAndCancelsWeekly() {
  withTempDir((ws) => {
    fs.mkdirSync(path.join(ws, 'skills'), { recursive: true });

    writeJson(path.join(ws, 'schedules/profiles/registry.json'), {
      version: 1,
      dataRoot: 'schedules/profiles',
      profiles: [{ profile_id: 'zian', type: 'self', display_name: 'Zian', aliases: ['z'] }]
    });

    writeJson(path.join(ws, 'schedules/profiles/zian/weekly.json'), {
      version: 1,
      profile_id: 'zian',
      recurrence: { type: 'every_week' },
      timezone: 'Asia/Singapore',
      weeks: {
        default: {
          mon: [{ title: 'Math', start_time: '09:00', end_time: '10:00', location: '', notes: '' }],
          tue: [], wed: [], thu: [], fri: [], sat: [], sun: []
        }
      }
    });

    writeJson(path.join(ws, 'schedules/profiles/zian/special_events.json'), {
      version: 1,
      profile_id: 'zian',
      events: [{ id: 'c', date: '2026-02-16', title: 'Holiday', cancels_weekly: true }]
    });

    const items = dayScheduleForProfile(ws, 'zian', new Date('2026-02-16T00:00:00'));
    assert.equal(items.some(i => i.title === 'Math'), false);
    assert.equal(items.some(i => i.title === 'Holiday'), true);
  });
})();

console.log('student-timetable tests: OK');
