-- CreateTable
CREATE TABLE "ABTest" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "problem1" TEXT NOT NULL,
    "problem2" TEXT NOT NULL,
    "problem3" TEXT NOT NULL,
    "problem1Answer" INTEGER NOT NULL,
    "problem2Answer" INTEGER NOT NULL,
    "problem3Answer" INTEGER NOT NULL
);

-- CreateTable
CREATE TABLE "TestSolve" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "testId" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "time" REAL NOT NULL,
    CONSTRAINT "TestSolve_testId_fkey" FOREIGN KEY ("testId") REFERENCES "ABTest" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
