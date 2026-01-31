# React Components

Package: `@thisispamela/react` (requires `@thisispamela/sdk`)

## Install

```bash
npm install @thisispamela/react @thisispamela/sdk
```

## Provider

Wrap your app with `PamelaProvider`:

```tsx
import { PamelaProvider } from '@thisispamela/react';

function App() {
  return (
    <PamelaProvider
      config={{ apiKey: 'pk_live_...', baseUrl: 'https://api.thisispamela.com' }}
    >
      <YourApp />
    </PamelaProvider>
  );
}
```

## CallButton + CallStatus

```tsx
import { CallButton, CallStatus } from '@thisispamela/react';
import { useState } from 'react';

function CallExample() {
  const [callId, setCallId] = useState<string | null>(null);

  return (
    <div>
      <CallButton
        to="+1234567890"
        task="Schedule a meeting for next week"
        onCallStart={(id) => setCallId(id)}
      >
        Call Now
      </CallButton>

      {callId && <CallStatus callId={callId} showTranscript={true} />}
    </div>
  );
}
```

## Components

- `PamelaProvider` - provides API config to children
- `CallButton` - initiates a call
- `CallStatus` - shows status, transcript, summary
- `TranscriptViewer` - displays transcript entries
- `VoiceOrb` - animated visual voice indicator
- `CallHistory` - list of previous calls

## Hook

```tsx
import { usePamela } from '@thisispamela/react';

const { client } = usePamela();
const call = await client.createCall({ to: '+1234567890', task: 'Custom task' });
```

## Styling

Components use Pamela's design system by default and support `className` overrides.
