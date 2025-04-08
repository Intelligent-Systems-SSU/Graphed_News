import { articleType } from './types';

class NewsApi {
  private apiUrl: string;

  constructor(apiUrl: string) {
    this.apiUrl = apiUrl;
  }

  private async fetchApi(route: string, params: Record<string, string> = {}) {
    const url = new URL(route, this.apiUrl);
    const response = await fetch(url, params);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  }

  public async getNewsList() {
    return this.fetchApi('/articles') as Promise<articleType[]>;
  }
}

export const newsApi = new NewsApi('https://advertisement-sega-turbo-cached.trycloudflare.com');
