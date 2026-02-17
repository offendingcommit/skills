#!/usr/bin/env node

/**
 * Apple Docs CLI - Query Apple Developer Documentation and WWDC Videos
 *
 * Direct integration with Apple's developer documentation APIs.
 * No external dependencies. All data from developer.apple.com.
 */

// ============ APPLE API CONSTANTS ============

const APPLE_URLS = {
  BASE: 'https://developer.apple.com',
  SEARCH: 'https://developer.apple.com/search/',
  DOCUMENTATION: 'https://developer.apple.com/documentation/',
  TUTORIALS_DATA: 'https://developer.apple.com/tutorials/data/',
  TECHNOLOGIES_JSON: 'https://developer.apple.com/tutorials/data/documentation/technologies.json',
  UPDATES_JSON: 'https://developer.apple.com/tutorials/data/documentation/Updates.json',
  TECHNOLOGY_OVERVIEWS_JSON: 'https://developer.apple.com/tutorials/data/documentation/TechnologyOverviews.json',
  SAMPLE_CODE_JSON: 'https://developer.apple.com/tutorials/data/documentation/SampleCode.json',
};

// WWDC - Apple's own pages
const WWDC_URLS = {
  SEARCH: 'https://developer.apple.com/search/',
  VIDEO_PAGE: (year, id) => `https://developer.apple.com/videos/play/wwdc${year}/${id}/`,
  VIDEOS_YEAR: (year) => `https://developer.apple.com/videos/wwdc${year}/`,
  ALL_VIDEOS: 'https://developer.apple.com/videos/all-videos/',
};

// Static WWDC metadata (public knowledge, updated yearly)
const WWDC_YEARS = [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];

const WWDC_TOPICS = [
  { name: 'Accessibility', slug: 'accessibility' },
  { name: 'App Store & Distribution', slug: 'app-store-distribution' },
  { name: 'Audio & Video', slug: 'audio-video' },
  { name: 'Augmented Reality', slug: 'augmented-reality' },
  { name: 'Design', slug: 'design' },
  { name: 'Developer Tools', slug: 'developer-tools' },
  { name: 'Extensions', slug: 'extensions' },
  { name: 'Graphics & Games', slug: 'graphics-games' },
  { name: 'Health & Fitness', slug: 'health-fitness' },
  { name: 'Machine Learning & AI', slug: 'machine-learning-ai' },
  { name: 'Maps & Location', slug: 'maps-location' },
  { name: 'Networking', slug: 'networking' },
  { name: 'Privacy & Security', slug: 'privacy-security' },
  { name: 'Safari & Web', slug: 'safari-web' },
  { name: 'Swift', slug: 'swift' },
  { name: 'SwiftUI & UI Frameworks', slug: 'swiftui-ui-frameworks' },
  { name: 'System Services', slug: 'system-services' },
  { name: 'Testing', slug: 'testing' },
  { name: 'visionOS', slug: 'visionos' },
  { name: 'Widgets & App Intents', slug: 'widgets-app-intents' },
];

// ============ HTTP CLIENT ============

async function httpFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15',
      'Accept': 'text/html,application/json,application/xhtml+xml',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response;
}

async function fetchJson(url) {
  const response = await httpFetch(url);
  return response.json();
}

async function fetchText(url) {
  const response = await httpFetch(url);
  return response.text();
}

// ============ SEARCH ============

async function searchAppleDocs(query, limit = 10) {
  const url = `${APPLE_URLS.SEARCH}?q=${encodeURIComponent(query)}`;
  const html = await fetchText(url);
  return parseSearchResults(html, limit, 'documentation');
}

function parseSearchResults(html, limit, type = null) {
  const results = [];
  const seen = new Set();

  // Match documentation links
  if (!type || type === 'documentation') {
    const docRegex = /<a[^>]+href="(\/documentation\/[^"]+)"[^>]*>([^<]+)<\/a>/gi;
    let match;
    while ((match = docRegex.exec(html)) !== null && results.length < limit) {
      const url = match[1];
      const title = match[2].trim().replace(/<[^>]*>/g, '');
      if (seen.has(url)) continue;
      seen.add(url);
      if (url.includes('/design/human-interface-guidelines/')) continue;
      if (url.includes('/download/')) continue;

      const frameworkMatch = url.match(/\/documentation\/([^/]+)\//);
      results.push({
        title: title || url.split('/').pop(),
        url: `https://developer.apple.com${url}`,
        framework: frameworkMatch ? frameworkMatch[1] : null,
        type: 'documentation'
      });
    }
  }

  // Match video links
  if (!type || type === 'video') {
    const videoRegex = /<a[^>]+href="(\/videos\/play\/wwdc(\d{4})\/(\d+)\/?)"[^>]*>([^<]*)<\/a>/gi;
    let match;
    while ((match = videoRegex.exec(html)) !== null && results.length < limit) {
      const url = match[1];
      const year = match[2];
      const id = match[3];
      const title = match[4].trim().replace(/<[^>]*>/g, '');
      if (seen.has(url)) continue;
      seen.add(url);

      results.push({
        title: title || `WWDC${year} Session ${id}`,
        url: `https://developer.apple.com${url}`,
        year: parseInt(year),
        id,
        type: 'video'
      });
    }
  }

  return results;
}

// ============ SYMBOL SEARCH ============

async function searchFrameworkSymbols(query, limit = 20) {
  const results = await searchAppleDocs(query, limit);
  return results;
}

// ============ FETCH DOC CONTENT ============

async function getAppleDocContent(url) {
  let jsonUrl = url;
  if (!url.includes('.json')) {
    const path = url.replace('https://developer.apple.com', '');
    jsonUrl = `https://developer.apple.com/tutorials/data${path}.json`;
  }

  try {
    const data = await fetchJson(jsonUrl);
    return formatDocContent(data);
  } catch {
    const html = await fetchText(url);
    return extractDocFromHtml(html, url);
  }
}

function formatDocContent(data) {
  let output = [];
  output.push(`# ${data.title || 'Documentation'}`);
  if (data.framework) output.push(`\nFramework: ${data.framework}`);
  if (data.platforms) output.push(`\nPlatforms: ${data.platforms.join(', ')}`);
  output.push('\n');

  if (data.description) output.push(`${data.description}\n`);
  if (data.content) output.push(`\n${extractTextFromContent(data.content)}`);

  if (data.topics?.length) {
    output.push('\n\nTopics:\n');
    data.topics.forEach(t => output.push(`  - ${t}`));
  }

  if (data.relationships?.length) {
    output.push('\n\nRelationships:\n');
    data.relationships.forEach(r => {
      output.push(`  - ${r.type}: ${r.name || r.url}`);
    });
  }

  return output.join('\n');
}

function extractDocFromHtml(html, url) {
  const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
  const title = titleMatch ? titleMatch[1] : 'Apple Documentation';

  const descMatch = html.match(/<meta[^>]+name="description"[^>]+content="([^"]+)"/i) ||
                   html.match(/<p[^>]+class="description"[^>]*>([^<]+)/i);
  const description = descMatch ? descMatch[1] : '';

  return `# ${title}\n\nURL: ${url}\n\n${description}`;
}

function extractTextFromContent(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) return content.map(c => extractTextFromContent(c)).join('\n');
  if (content.text) return content.text;
  return JSON.stringify(content);
}

// ============ LIST TECHNOLOGIES ============

async function listTechnologies() {
  const data = await fetchJson(APPLE_URLS.TECHNOLOGIES_JSON);
  return data;
}

// ============ RELATED APIS ============

async function getRelatedApis(symbolName) {
  const results = await searchAppleDocs(symbolName, 5);
  return results;
}

// ============ PLATFORM COMPATIBILITY ============

async function getPlatformCompatibility(symbolName) {
  const results = await searchAppleDocs(`${symbolName} platform compatibility`, 5);
  return results;
}

// ============ SIMILAR APIS ============

async function findSimilarApis(symbolName) {
  const results = await searchAppleDocs(`${symbolName} alternative replacement`, 5);
  return results;
}

// ============ DOCUMENTATION UPDATES ============

async function getDocumentationUpdates(limit = 10) {
  try {
    const data = await fetchJson(APPLE_URLS.UPDATES_JSON);
    return (data.updates || data.slice(0, limit));
  } catch {
    return [{ error: 'Could not fetch updates' }];
  }
}

// ============ TECHNOLOGY OVERVIEWS ============

async function getTechnologyOverviews(technology) {
  try {
    const data = await fetchJson(APPLE_URLS.TECHNOLOGY_OVERVIEWS_JSON);
    const filtered = data.filter(t =>
      t.name?.toLowerCase().includes(technology.toLowerCase()) ||
      t.title?.toLowerCase().includes(technology.toLowerCase())
    );
    return filtered;
  } catch {
    return [{ error: 'Could not fetch technology overviews' }];
  }
}

// ============ SAMPLE CODE ============

async function getSampleCode(technology, limit = 10) {
  try {
    const data = await fetchJson(APPLE_URLS.SAMPLE_CODE_JSON);
    const filtered = (data.sampleCode || data)
      .filter(s => s.title?.toLowerCase().includes(technology.toLowerCase()))
      .slice(0, limit);
    return filtered;
  } catch {
    return [{ error: 'Could not fetch sample code' }];
  }
}

// ============ WWDC - APPLE'S OWN PAGES ============

async function searchWwdcVideos(query, year = null, limit = 10) {
  // Use Apple's own search with video type filtering
  const searchQuery = year ? `WWDC ${year} ${query}` : `WWDC ${query}`;
  const url = `${WWDC_URLS.SEARCH}?q=${encodeURIComponent(searchQuery)}&type=Videos`;
  const html = await fetchText(url);

  // Parse video results from search HTML
  const results = [];
  const seen = new Set();

  // Match video links from Apple's search results
  const videoRegex = /<a[^>]+href="(\/videos\/play\/wwdc(\d{4})\/(\d+)\/?)"[^>]*>([\s\S]*?)<\/a>/gi;
  let match;
  while ((match = videoRegex.exec(html)) !== null && results.length < limit) {
    const path = match[1];
    const videoYear = parseInt(match[2]);
    const id = match[3];
    const rawTitle = match[4].replace(/<[^>]*>/g, '').trim();

    if (year && videoYear !== parseInt(year)) continue;

    const key = `${videoYear}-${id}`;
    if (seen.has(key)) continue;
    seen.add(key);

    results.push({
      id,
      year: videoYear,
      title: rawTitle || `Session ${id}`,
      url: `https://developer.apple.com${path}`,
    });
  }

  // Fallback: try broader regex if first pass found nothing
  if (results.length === 0) {
    const broadRegex = /href="[^"]*\/videos\/play\/wwdc(\d{4})\/(\d+)\/?"/gi;
    const titleRegex = /<h\d[^>]*>([^<]+)<\/h\d>/gi;
    const titles = [];
    let titleMatch;
    while ((titleMatch = titleRegex.exec(html)) !== null) {
      titles.push(titleMatch[1].trim());
    }

    let idx = 0;
    while ((match = broadRegex.exec(html)) !== null && results.length < limit) {
      const videoYear = parseInt(match[1]);
      const id = match[2];
      if (year && videoYear !== parseInt(year)) continue;

      const key = `${videoYear}-${id}`;
      if (seen.has(key)) continue;
      seen.add(key);

      results.push({
        id,
        year: videoYear,
        title: titles[idx] || `WWDC${videoYear} Session ${id}`,
        url: `https://developer.apple.com/videos/play/wwdc${videoYear}/${id}/`,
      });
      idx++;
    }
  }

  return results;
}

async function getWwdcVideoDetails(videoId, includeTranscript = true) {
  // Parse video ID (format: "2024-100" or "2024 100")
  const match = videoId.match(/(\d{4})[-_\s]?(\d+)/);
  if (!match) {
    return { error: 'Invalid video ID format. Use format: YYYY-NNN (e.g., 2024-100)' };
  }

  const year = match[1];
  const id = match[2];
  const url = WWDC_URLS.VIDEO_PAGE(year, id);

  try {
    const html = await fetchText(url);
    return parseWwdcVideoPage(html, year, id, url, includeTranscript);
  } catch (err) {
    return { error: `Could not fetch video ${year}-${id}: ${err.message}` };
  }
}

function parseWwdcVideoPage(html, year, id, url, includeTranscript) {
  let output = [];

  // Extract title
  const titleMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i) ||
                    html.match(/<title>([^<|]+)/i);
  const title = titleMatch ? titleMatch[1].trim() : `WWDC${year} Session ${id}`;

  output.push(`# ${title}`);
  output.push(`\nYear: ${year} | Session: ${id}`);
  output.push(`URL: ${url}`);

  // Extract description
  const descMatch = html.match(/<meta[^>]+name="description"[^>]+content="([^"]+)"/i);
  if (descMatch) {
    output.push(`\n## Description\n${descMatch[1]}`);
  }

  // Extract description from page body
  const bodyDescMatch = html.match(/<p[^>]+class="[^"]*description[^"]*"[^>]*>([\s\S]*?)<\/p>/i);
  if (bodyDescMatch) {
    const desc = bodyDescMatch[1].replace(/<[^>]*>/g, '').trim();
    if (desc) output.push(`\n${desc}`);
  }

  // Extract related resources/links
  const relatedLinks = [];
  const relatedRegex = /href="(\/videos\/play\/wwdc\d{4}\/\d+\/?)"[^>]*>([^<]+)/gi;
  let relMatch;
  while ((relMatch = relatedRegex.exec(html)) !== null) {
    const relUrl = relMatch[1];
    const relTitle = relMatch[2].trim();
    if (relUrl !== `/videos/play/wwdc${year}/${id}/`) {
      relatedLinks.push({ title: relTitle, url: `https://developer.apple.com${relUrl}` });
    }
  }

  if (relatedLinks.length > 0) {
    output.push(`\n## Related Sessions`);
    relatedLinks.forEach(r => output.push(`  - ${r.title} (${r.url})`));
  }

  // Extract topics/tags
  const topicMatches = [];
  const topicRegex = /data-tag="([^"]+)"/gi;
  let tMatch;
  while ((tMatch = topicRegex.exec(html)) !== null) {
    topicMatches.push(tMatch[1]);
  }
  if (topicMatches.length > 0) {
    output.push(`\nTopics: ${topicMatches.join(', ')}`);
  }

  // Look for transcript section
  if (includeTranscript) {
    const transcriptMatch = html.match(/<section[^>]+class="[^"]*transcript[^"]*"[^>]*>([\s\S]*?)<\/section>/i);
    if (transcriptMatch) {
      const transcript = transcriptMatch[1]
        .replace(/<[^>]*>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
      if (transcript) {
        output.push(`\n## Transcript\n${transcript.substring(0, 2000)}...`);
        output.push(`\n[Full transcript at: ${url}]`);
      }
    }
  }

  // Extract download links
  const downloadLinks = [];
  const dlRegex = /href="([^"]+\.(mp4|pdf|zip|key))[^"]*"/gi;
  let dlMatch;
  while ((dlMatch = dlRegex.exec(html)) !== null) {
    downloadLinks.push(dlMatch[1]);
  }
  if (downloadLinks.length > 0) {
    output.push(`\n## Downloads`);
    downloadLinks.forEach(d => output.push(`  - ${d}`));
  }

  return output.join('\n');
}

function listWwdcTopics() {
  return WWDC_TOPICS;
}

function listWwdcYears() {
  return {
    years: WWDC_YEARS,
    totalYears: WWDC_YEARS.length
  };
}

// ============ OUTPUT FORMATTING ============

const colors = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m',
  red: '\x1b[31m', cyan: '\x1b[36m', magenta: '\x1b[35m', white: '\x1b[37m'
};

function log(text = '', color = 'reset') {
  console.log(`${colors[color]}${text}${colors.reset}`);
}

function logError(text) {
  console.error(`${colors.red}Error: ${text}${colors.reset}`);
}

function outputJson(data) {
  console.log(JSON.stringify(data, null, 2));
}

function outputResults(results, title) {
  if (!results || results.length === 0) {
    log('\nNo results found.', 'yellow');
    return;
  }

  log(`\n${title}`, 'bright');
  log('='.repeat(50), 'dim');

  results.forEach((r, i) => {
    if (r.title || r.name) {
      log(`\n${i + 1}. ${r.title || r.name}`, 'cyan');
      if (r.framework) log(`   Framework: ${r.framework}`, 'dim');
      if (r.year) log(`   Year: ${r.year}`, 'dim');
      if (r.topics) log(`   Topics: ${(Array.isArray(r.topics) ? r.topics.join(', ') : r.topics)}`, 'dim');
      if (r.slug) log(`   Slug: ${r.slug}`, 'dim');
      if (r.url) log(`   URL: ${r.url}`, 'dim');
    } else {
      log(`\n${JSON.stringify(r)}`);
    }
  });
}

// ============ COMMANDS ============

async function cmdSearch(query, options = {}) {
  if (!query) {
    logError('Search query required');
    log('Usage: apple-docs search "SwiftUI animation"');
    process.exit(1);
  }

  log(`\nSearching Apple docs for: "${query}"`, 'bright');
  const results = await searchAppleDocs(query, options.limit || 10);
  outputResults(results, 'Search Results');
}

async function cmdSymbols(query, options = {}) {
  if (!query) {
    logError('Symbol query required');
    log('Usage: apple-docs symbols "UITableView"');
    process.exit(1);
  }

  log(`\nSearching for symbols: "${query}"`, 'bright');
  const results = await searchFrameworkSymbols(query, options.limit || 20);
  outputResults(results, 'Symbol Results');
}

async function cmdDoc(path) {
  if (!path) {
    logError('Documentation path required');
    log('Usage: apple-docs doc "/documentation/swiftui/view"');
    process.exit(1);
  }

  const url = path.startsWith('http') ? path : `https://developer.apple.com${path}`;
  log(`\nFetching documentation: ${url}`, 'bright');
  const content = await getAppleDocContent(url);
  log(`\n${content}`);
}

async function cmdTech() {
  log('\nListing Apple technologies...', 'bright');
  const data = await listTechnologies();
  outputJson(data);
}

async function cmdApis(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs apis "UIViewController"');
    process.exit(1);
  }

  log(`\nFinding related APIs for: "${symbol}"`, 'bright');
  const results = await getRelatedApis(symbol);
  outputResults(results, 'Related APIs');
}

async function cmdPlatform(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs platform "UIScrollView"');
    process.exit(1);
  }

  log(`\nChecking platform compatibility for: "${symbol}"`, 'bright');
  const results = await getPlatformCompatibility(symbol);
  outputResults(results, 'Platform Compatibility');
}

async function cmdSimilar(symbol) {
  if (!symbol) {
    logError('Symbol name required');
    log('Usage: apple-docs similar "UIPickerView"');
    process.exit(1);
  }

  log(`\nFinding similar/alternative APIs for: "${symbol}"`, 'bright');
  const results = await findSimilarApis(symbol);
  outputResults(results, 'Similar APIs');
}

async function cmdUpdates(options = {}) {
  log('\nFetching documentation updates...', 'bright');
  const updates = await getDocumentationUpdates(options.limit || 10);
  outputJson(updates);
}

async function cmdOverview(technology) {
  if (!technology) {
    logError('Technology name required');
    log('Usage: apple-docs overview "SwiftUI"');
    process.exit(1);
  }

  log(`\nFetching technology overview: ${technology}`, 'bright');
  const overviews = await getTechnologyOverviews(technology);
  outputJson(overviews);
}

async function cmdSamples(technology, options = {}) {
  if (!technology) {
    logError('Technology name required');
    log('Usage: apple-docs samples "SwiftUI"');
    process.exit(1);
  }

  log(`\nSearching sample code for: ${technology}`, 'bright');
  const samples = await getSampleCode(technology, options.limit || 10);
  outputJson(samples);
}

async function cmdWwdcSearch(query, options = {}) {
  if (!query) {
    logError('WWDC search query required');
    log('Usage: apple-docs wwdc-search "async await"');
    process.exit(1);
  }

  log(`\nSearching WWDC videos for: "${query}"`, 'bright');
  const results = await searchWwdcVideos(query, options.year, options.limit || 10);
  outputResults(results, 'WWDC Videos');
}

async function cmdWwdcVideo(id, options = {}) {
  if (!id) {
    logError('WWDC video ID required');
    log('Usage: apple-docs wwdc-video 2024-100');
    process.exit(1);
  }

  log(`\nFetching WWDC video details: ${id}`, 'bright');
  const details = await getWwdcVideoDetails(id, options.transcript !== false);
  if (typeof details === 'string') {
    log(`\n${details}`);
  } else {
    outputJson(details);
  }
}

async function cmdWwdcTopics() {
  log('\nWWDC Topic Categories:', 'bright');
  const topics = listWwdcTopics();
  outputResults(topics, 'WWDC Topics');
}

async function cmdWwdcYears() {
  const data = listWwdcYears();

  log(`\nWWDC Years (${data.totalYears} conferences):`, 'bright');
  log('='.repeat(40), 'dim');

  data.years.forEach(year => {
    log(`  ${year}`, 'cyan');
  });
}

// ============ HELP ============

function showHelp() {
  log(`
${colors.bright}Apple Docs CLI${colors.reset} - Query Apple Developer Documentation and WWDC Videos
${colors.dim}Direct integration with developer.apple.com${colors.reset}

${colors.bright}SETUP:${colors.reset}
  No setup required - works out of the box.

${colors.bright}SEARCH COMMANDS:${colors.reset}
  apple-docs search "query"              Search Apple Developer Documentation
  apple-docs symbols "UIView"            Search framework classes, structs, protocols
  apple-docs doc "/path/to/doc"          Get detailed documentation by path

${colors.bright}API EXPLORATION:${colors.reset}
  apple-docs apis "UIViewController"     Find related APIs
  apple-docs platform "UIScrollView"     Check platform compatibility
  apple-docs similar "UIPickerView"      Find similar/recommended alternatives

${colors.bright}TECHNOLOGY BROWSING:${colors.reset}
  apple-docs tech                        List all Apple technologies
  apple-docs overview "SwiftUI"          Get technology overview guide
  apple-docs samples "SwiftUI"           Find sample code projects
  apple-docs updates                     Latest documentation updates

${colors.bright}WWDC VIDEOS:${colors.reset}
  apple-docs wwdc-search "async"         Search WWDC sessions (2014-2025)
  apple-docs wwdc-video 2024-100         Get video details and transcript
  apple-docs wwdc-topics                 List WWDC topic categories
  apple-docs wwdc-years                  List available WWDC years

${colors.bright}OPTIONS:${colors.reset}
  --limit <n>     Limit results (default varies)
  --category      Filter by technology category
  --framework     Filter by framework name
  --year          Filter by WWDC year
  --no-transcript Skip transcript for WWDC videos

${colors.bright}EXAMPLES:${colors.reset}
  ${colors.dim}# Search for SwiftUI animations${colors.reset}
  apple-docs search "SwiftUI animation"

  ${colors.dim}# Find UITableView delegate methods${colors.reset}
  apple-docs symbols "UITableViewDelegate"

  ${colors.dim}# Check iOS version support for Vision framework${colors.reset}
  apple-docs platform "VNRecognizeTextRequest"

  ${colors.dim}# Find WWDC sessions about async/await${colors.reset}
  apple-docs wwdc-search "async await"

  ${colors.dim}# Get a specific WWDC video${colors.reset}
  apple-docs wwdc-video 2024-100

  ${colors.dim}# List all available WWDC years${colors.reset}
  apple-docs wwdc-years
  `);
}

// ============ MAIN ============

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help' || command === 'help' || command === '-h') {
    showHelp();
    return;
  }

  // Parse options
  const options = {};
  let query = null;
  let i = 1;

  while (i < args.length) {
    const arg = args[i];

    if (arg.startsWith('--')) {
      const key = arg.substring(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const valueOptions = ['limit', 'category', 'framework', 'year'];
      if (valueOptions.includes(key)) {
        options[key] = args[i + 1];
        i += 2;
      } else if (key === 'noTranscript') {
        options.transcript = false;
        i++;
      } else {
        options[key] = true;
        i++;
      }
    } else if (!arg.startsWith('-') && !['search', 'symbols', 'wwdc-search'].includes(command)) {
      if (command === 'doc') {
        options.path = arg;
      } else if (command === 'apis' || command === 'platform' || command === 'similar') {
        options.symbol = arg;
      } else if (command === 'tech' || command === 'overview') {
        options.technology = arg;
      } else if (command === 'samples') {
        options.technology = arg;
      } else if (command === 'wwdc-video') {
        options.id = arg;
      }
      i++;
    } else {
      i++;
    }
  }

  // Handle positional query for search commands
  if (command === 'search' || command === 'symbols' || command === 'wwdc-search') {
    query = args.slice(1).find(a => !a.startsWith('-')) || '';
  }

  try {
    switch (command) {
      case 'search': await cmdSearch(query, options); break;
      case 'doc': await cmdDoc(options.path, options); break;
      case 'tech': await cmdTech(options); break;
      case 'symbols': await cmdSymbols(query, options); break;
      case 'apis': await cmdApis(options.symbol, options); break;
      case 'platform': await cmdPlatform(options.symbol, options); break;
      case 'similar': await cmdSimilar(options.symbol, options); break;
      case 'updates': await cmdUpdates(options); break;
      case 'overview': await cmdOverview(options.technology, options); break;
      case 'samples': await cmdSamples(options.technology, options); break;
      case 'wwdc-search': await cmdWwdcSearch(query, options); break;
      case 'wwdc-video': await cmdWwdcVideo(options.id, options); break;
      case 'wwdc-topics': await cmdWwdcTopics(); break;
      case 'wwdc-years': await cmdWwdcYears(); break;
      default:
        logError(`Unknown command: ${command}`);
        log('Run: apple-docs --help');
        process.exit(1);
    }
  } catch (err) {
    logError(err.message);
    process.exit(1);
  }
}

main().catch(err => {
  logError(err.message);
  process.exit(1);
});
