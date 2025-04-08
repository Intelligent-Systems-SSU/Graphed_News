export interface articleType {
  id: number;
  url: string;
  title: string;
  content: string;
  crawled_date: string;
  keywords: string;
  published_date: string;
}

export interface articleBackgroundType {
  id: number;
  article_id: number;
  topic: string;
  content: string;
}
