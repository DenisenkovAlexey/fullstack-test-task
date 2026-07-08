import type { Metadata } from "next";
import { BootstrapProvider } from "../ui/providers/BootstrapProvider";
import { AppContainer } from "../ui/components/AppContainer";

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: 'Тестовое задание Fullstack',
    description: 'Тестовое задание Fullstack',
  };
}

export default async function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang='ru'>
      <head>
        <link rel="icon" href="/public/favicon.ico" sizes="any" />
      </head>
      <body>
        <BootstrapProvider>
          <AppContainer>
            {children}
          </AppContainer>
        </BootstrapProvider>
      </body>
    </html>
  );
}
