"use client";

import Image from "next/image";

export default function GlobalError({ error }: { error: Error }) {
  return (
    <html>
      <body>
        <div
          style={{
            position: "fixed",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "1rem",
          }}
        >
          <Image src="/error.svg" alt="Error" width={256} height={256} />
        </div>
      </body>
    </html>
  );
}
