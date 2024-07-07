import Head from 'next/head';
import Chat from '@/components/Chat';

const Home = () => {
  return (
    <div>
      <Head>
        <title>Cognitus AI Chat</title>
        <meta name="description" content="Basic chat interface using Next.js and Tailwind CSS" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <Chat />
      </main>
    </div>
  );
};

export default Home;
