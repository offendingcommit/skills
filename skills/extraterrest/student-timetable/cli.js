#!/usr/bin/env node

const { resolveWorkspaceRoot } = require('./workspace_root.js');
const { loadProfilesRegistry, resolveProfile, clarifyProfileMessage } = require('./profiles_registry.js');
const { dayScheduleForProfile, weekScheduleForProfile, todayDate } = require('./student_timetable_service.js');
const { addDays, formatISODate } = require('./date_utils.js');
const { interactiveInit } = require('./init.js');
const { migrateKidSchedule, migrateLegacyZian } = require('./migrate.js');

function usage() {
  process.stderr.write('student-timetable CLI\n');
  console.log('');
  console.log('Usage:');
  console.log('  node skills/student-timetable/cli.js <command> [--profile <id|name|alias>]');
  console.log('');
  console.log('Commands:');
  console.log('  init');
  console.log('  today');
  console.log('  tomorrow');
  console.log('  this_week');
  console.log('  next_week');
  console.log('  migrate kid-schedule [--dry-run]');
  console.log('  migrate legacy-zian [--dry-run]');
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--profile') {
      args.profile = argv[i + 1];
      i++;
    } else if (a === '--date') {
      args.date = argv[i + 1];
      i++;
    } else if (a === '--dry-run') {
      args.dryRun = true;
    } else {
      args._.push(a);
    }
  }
  return args;
}

function printDay(items, label) {
  console.log(label);
  if (!items.length) {
    console.log('  (no items)');
    return;
  }
  for (const it of items) {
    const time = it.start_time ? `${it.start_time}-${it.end_time || ''}`.replace(/-$/, '') : 'TBD';
    const notes = it.notes ? ` | ${it.notes}` : '';
    console.log(`  ${time} | ${it.title}${notes} [${it.source}]`);
  }
}

async function main() {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);
  const command = args._[0];

  if (!command) {
    usage();
    process.exit(1);
  }

  const workspaceRoot = resolveWorkspaceRoot();

  if (command === 'init') {
    await interactiveInit(workspaceRoot);
    return;
  }

  if (command === 'migrate') {
    const which = args._[1];
    if (which === 'kid-schedule') {
      const report = migrateKidSchedule(workspaceRoot, { dryRun: !!args.dryRun });
      console.log(JSON.stringify(report, null, 2));
      return;
    }
    if (which === 'legacy-zian') {
      const report = migrateLegacyZian(workspaceRoot, { dryRun: !!args.dryRun });
      console.log(JSON.stringify(report, null, 2));
      return;
    }
    usage();
    process.exit(1);
  }

  const registry = loadProfilesRegistry(workspaceRoot);
  const allowDefaultToSelf = true;
  const resolved = resolveProfile(registry, args.profile, { allowDefaultToSelf });
  if (!resolved.ok) {
    resolved.input = args.profile;
    console.log(clarifyProfileMessage(resolved));
    process.exit(2);
  }

  const profile = resolved.profile;
  const today = todayDate();

  if (command === 'today') {
    const items = dayScheduleForProfile(workspaceRoot, profile.profile_id, today);
    printDay(items, `${profile.display_name || profile.profile_id} - Today (${formatISODate(today)})`);
    return;
  }

  if (command === 'tomorrow') {
    const d = addDays(today, 1);
    const items = dayScheduleForProfile(workspaceRoot, profile.profile_id, d);
    printDay(items, `${profile.display_name || profile.profile_id} - Tomorrow (${formatISODate(d)})`);
    return;
  }

  if (command === 'this_week' || command === 'next_week') {
    const which = command === 'next_week' ? 'next' : 'this';
    const wk = weekScheduleForProfile(workspaceRoot, profile.profile_id, today, which);
    console.log(`${profile.display_name || profile.profile_id} - ${command} (week of ${wk.week_start})`);
    for (const day of wk.days) {
      console.log('');
      printDay(day.items, `${day.weekday} (${day.date})`);
    }
    return;
  }

  usage();
  process.exit(1);
}

if (require.main === module) {
  main().catch(err => {
    console.error(err && err.stack ? err.stack : String(err));
    process.exit(1);
  });
}
