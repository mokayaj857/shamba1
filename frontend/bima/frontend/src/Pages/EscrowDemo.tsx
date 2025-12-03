import Layout from '@/components/Layout';

export default function EscrowDemo(): JSX.Element {
  return (
    <Layout showHeader>
      <div className="max-w-4xl mx-auto py-20 px-4">
        <h1 className="text-3xl font-bold mb-4">Escrow Demo (Disabled)</h1>
        <p className="text-muted-foreground mb-6">
          The escrow demo page has been added as a placeholder. Wallet-connected features are disabled in this build.
        </p>
        <div className="rounded-md p-6 border border-border/50 bg-card/50">
          <p>If you previously relied on an interactive wallet demo, that functionality has been removed.</p>
        </div>
      </div>
    </Layout>
  );
}
