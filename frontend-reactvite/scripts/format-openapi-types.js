import fs from 'fs';
import path from 'path';

function formatOpenAPIFiles() {
  console.log('🔍 Formatting OpenAPI generated files...');
  
  const apiDir = path.join(process.cwd(), 'src', 'lib', 'api', 'axios-client');
  
  if (!fs.existsSync(apiDir)) {
    console.error('❌ API directory not found:', apiDir);
    return;
  }
  
  // Define specific line replacements for each file
  const replacements = {
    'common.ts': [
      {
        search: 'import { RequiredError, RequestArgs } from "./base";',
        replace: "import { RequiredError, type RequestArgs } from './base';"
      },
      {
        search: "import { AxiosInstance, AxiosResponse } from 'axios';",
        replace: "import type { AxiosInstance, AxiosResponse } from 'axios';"
      }
    ],
    'api.ts': [
      {
        search: "import globalAxios, { AxiosPromise, AxiosInstance, AxiosRequestConfig } from 'axios';",
        replace: "import globalAxios, { type AxiosPromise, type AxiosInstance, type AxiosRequestConfig } from 'axios';"
      },
      {
        search: "import { BASE_PATH, COLLECTION_FORMATS, RequestArgs, BaseAPI, RequiredError } from './base';",
        replace: "import { BASE_PATH, COLLECTION_FORMATS, type RequestArgs, BaseAPI, RequiredError } from './base';"
      }
    ],
    'base.ts': [
      {
        search: "import globalAxios, { AxiosPromise, AxiosInstance, AxiosRequestConfig } from 'axios';",
        replace: "import globalAxios, { type AxiosPromise, type AxiosInstance, type AxiosRequestConfig } from 'axios';"
      }
    ]
  };
  
  Object.keys(replacements).forEach(filename => {
    const filePath = path.join(apiDir, filename);
    if (fs.existsSync(filePath)) {
      let content = fs.readFileSync(filePath, 'utf-8');
      let modified = false;
      
      replacements[filename].forEach(({ search, replace }) => {
        if (content.includes(search)) {
          content = content.replace(search, replace);
          modified = true;
          console.log(`✏️  Fixed import in ${filename}: ${search}`);
        }
      });
      
      if (modified) {
        fs.writeFileSync(filePath, content, 'utf-8');
        console.log(`✅ Updated ${filename}`);
      } else {
        console.log(`ℹ️  No changes needed for ${filename}`);
      }
    }
  });
  
  console.log('✅ OpenAPI files formatting completed!');
}

formatOpenAPIFiles();
