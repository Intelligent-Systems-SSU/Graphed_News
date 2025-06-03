-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_TestSolve" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "testId" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "time" REAL,
    CONSTRAINT "TestSolve_testId_fkey" FOREIGN KEY ("testId") REFERENCES "ABTest" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_TestSolve" ("id", "name", "testId", "time") SELECT "id", "name", "testId", "time" FROM "TestSolve";
DROP TABLE "TestSolve";
ALTER TABLE "new_TestSolve" RENAME TO "TestSolve";
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;
