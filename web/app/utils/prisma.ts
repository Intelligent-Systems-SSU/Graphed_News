import { PrismaD1 } from '@prisma/adapter-d1';
import { PrismaClient } from '@prisma/client';

export const getPrismaClient = ({ env }: { env: Env }) => {
  const adapter = new PrismaD1(env.DB);
  return new PrismaClient({ adapter });
};
