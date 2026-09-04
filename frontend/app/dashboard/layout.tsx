import localFont from "next/font/local";

const nippo = localFont({
  src: [
    {
      path: "../../public/fonts/nippo/Nippo-Extralight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "../../public/fonts/nippo/Nippo-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "../../public/fonts/nippo/Nippo-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../public/fonts/nippo/Nippo-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../public/fonts/nippo/Nippo-Bold.woff2",
      weight: "700",
      style: "normal",
    },
  ],
  variable: "--font-nippo",
  display: "swap",
});

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={`${nippo.variable} ${nippo.className}`} style={{ fontFamily: "var(--font-nippo), sans-serif" }}>
      {children}
    </div>
  );
}
