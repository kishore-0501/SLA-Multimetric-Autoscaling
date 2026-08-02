import http from 'k6/http';
import { sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '1m', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  http.get('http://k8s-slademo-slagatew-236c75dd7b-a87843532616133b.elb.eu-west-1.amazonaws.com/');
  sleep(1);
}
