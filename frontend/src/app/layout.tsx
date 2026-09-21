import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Recruitment Pro | Enterprise Recruitment Platform',
  description: 'Enterprise recruitment platform — job management, applicant tracking, candidate ingestion, and interview operations.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className={`${inter.className} bg-[#F8F9FB] text-[#111827] antialiased min-h-screen flex flex-col`}>
        {children}
      </body>
    </html>
  );
}
