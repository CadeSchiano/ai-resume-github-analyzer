export type RoleGuide = {
  slug: string;
  title: string;
  summary: string;
  coreSkills: string[];
  differentiators: string[];
  projectProof: string;
};

export const roleGuides: RoleGuide[] = [
  {
    slug: "software-engineer-intern",
    title: "Software Engineer Intern",
    summary: "Build a dependable foundation, then show that you can turn it into a complete, explainable project.",
    coreSkills: ["One programming language you can explain well, such as Python, Java, JavaScript, TypeScript, C++, or Java", "A practical application technology, such as React, Node.js, FastAPI, Django, Flask, Spring, or REST APIs", "Git workflows and the ability to read, test, and improve existing code"],
    differentiators: ["One finished project with a clear problem, a working demo, and setup instructions", "Thoughtful tradeoffs you can explain, rather than a long list of tools", "Evidence of iteration, such as tests, bug fixes, meaningful commits, or user feedback"],
    projectProof: "A small deployed app with a focused README, a few tests, and a clear explanation of what you personally built is often more useful than several unfinished tutorials.",
  },
  {
    slug: "software-engineer",
    title: "Software Engineer",
    summary: "Show reliable coding fundamentals along with the ability to build and maintain a complete product feature.",
    coreSkills: ["A primary programming language and a framework you can use confidently", "Data structures, debugging, testing, and practical API or application development", "A data or deployment technology, such as PostgreSQL, MySQL, MongoDB, Docker, AWS, or Azure"],
    differentiators: ["Clear ownership of a feature from problem to outcome", "Tests, error handling, documentation, and maintainable project structure", "A concise explanation of performance, reliability, or product tradeoffs"],
    projectProof: "Show a project that includes real application flow, not only an interface. Explain the architecture, data flow, and the choices you would revisit with more time.",
  },
  {
    slug: "backend-developer",
    title: "Backend Developer",
    summary: "Focus on dependable services, clear data modeling, and APIs that other developers can use safely.",
    coreSkills: ["A backend language, such as Python, Java, Go, C#, or Node.js", "An API framework or protocol, such as REST APIs, GraphQL, FastAPI, Django, Flask, Express, or Spring", "A database technology, such as PostgreSQL, MySQL, MongoDB, or Redis"],
    differentiators: ["Input validation, authentication, authorization, and useful error responses", "Well-designed schema choices, migrations, and clear API documentation", "Tests for important paths plus logging, monitoring, caching, or performance reasoning where appropriate"],
    projectProof: "Build an API that someone else can run from the README, with example requests, a database-backed feature, and a short explanation of security and failure cases.",
  },
  {
    slug: "frontend-developer",
    title: "Frontend Developer",
    summary: "Demonstrate that you can make an interface accurate, accessible, responsive, and connected to real data.",
    coreSkills: ["JavaScript or TypeScript", "A frontend framework, such as React, Next.js, Vue, or Angular", "HTML, CSS, component design, state management, and API integration"],
    differentiators: ["Accessibility, responsive design, loading and error states, and polished interaction details", "A sensible component structure instead of one large page component", "Performance awareness, interface tests, or a documented design system"],
    projectProof: "A deployed responsive interface with screenshots, live data or a realistic API, and a README that explains the component and state choices is strong public evidence.",
  },
  {
    slug: "full-stack-developer",
    title: "Full-Stack Developer",
    summary: "Show that you can connect a clean user experience to a trustworthy backend and data layer.",
    coreSkills: ["JavaScript or TypeScript and a frontend framework such as React or Next.js", "A backend technology such as Node.js, Python, FastAPI, Django, Flask, Express, Spring, or REST APIs", "A database technology, such as PostgreSQL, MySQL, MongoDB, or Redis"],
    differentiators: ["Authentication, authorization, validation, and a coherent data model", "A clear boundary between client, server, and database responsibilities", "Deployment, end-to-end testing, or a short architecture walkthrough"],
    projectProof: "A focused product with a real user flow, persistent data, and a deployable setup is more persuasive than a collection of disconnected demos.",
  },
  {
    slug: "mobile-developer",
    title: "Mobile Developer",
    summary: "Demonstrate platform awareness and an app experience that feels considered on a real device.",
    coreSkills: ["A mobile language such as Swift, Kotlin, Dart, JavaScript, or TypeScript", "A mobile framework or platform, such as React Native, Flutter, Android, or iOS", "Navigation, local state, network requests, and device-aware interface design"],
    differentiators: ["Thoughtful offline, loading, permissions, and error states", "A testing approach plus attention to platform conventions and accessibility", "A build or release workflow and evidence that the experience was tested on a device"],
    projectProof: "Include a short demo video or screenshots, setup instructions, and a clear explanation of the app flow. A working device experience is especially valuable here.",
  },
  {
    slug: "ai-ml",
    title: "AI/ML",
    summary: "Start with sound Python and data foundations, then make your model work measurable and reproducible.",
    coreSkills: ["Python", "Data tools such as NumPy and pandas", "A machine-learning library such as scikit-learn, PyTorch, or TensorFlow"],
    differentiators: ["A well-framed problem, relevant dataset choices, and a meaningful evaluation method", "Reproducible training or inference steps with clear dependencies", "An explanation of model limits, failure cases, fairness, cost, latency, or deployment tradeoffs"],
    projectProof: "Show the full path from data to evaluation to a usable result. A notebook alone is less persuasive than a documented, reproducible project with measured outcomes.",
  },
];

export const roleGuideBySlug = Object.fromEntries(roleGuides.map((guide) => [guide.slug, guide]));
export const roleSlugByTitle = Object.fromEntries(roleGuides.map((guide) => [guide.title, guide.slug]));
