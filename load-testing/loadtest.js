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
  http.get('http://k8s-slademo-podinfo-15982e669e-3f1392bbb43be6e2.elb.eu-west-1.amazonaws.com:9898/');
  sleep(1);
}