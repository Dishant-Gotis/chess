import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
    subsets: ["latin"],
    variable: "--font-inter",
    display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
    subsets: ["latin"],
    variable: "--font-jetbrains",
    display: "swap",
});

export const metadata = {
    title: "Chess — Play Online",
    description: "A beautiful, full-featured chess game with AI opponent, move history, and timers.",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
            <body>{children}</body>
        </html>
    );
}
