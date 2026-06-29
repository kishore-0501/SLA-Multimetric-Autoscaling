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
  http.get('http://k8s-slademo-slagatew-26fc8a4e00-c4f42871e24f938f.elb.eu-west-1.amazonaws.com/');
  sleep(1);
}
