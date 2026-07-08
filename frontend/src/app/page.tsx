import { ApiUrlProvider } from '../ui/providers/ApiUrlProvider';
import { getApiUrl } from '../shared/config/env';
import { HomePage } from '../features/home/HomePage';

export default function Page() {
  const apiUrl = getApiUrl();

  return (
    <ApiUrlProvider value={apiUrl}>
      <HomePage />
    </ApiUrlProvider>
  );
}
