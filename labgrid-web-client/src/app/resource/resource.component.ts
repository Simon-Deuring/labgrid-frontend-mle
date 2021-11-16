import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { ResourceService } from '../services/resource.service';
import { Resource } from 'src/models/resource';

@Component({
  selector: 'app-resource',
  templateUrl: './resource.component.html',
  styleUrls: ['./resource.component.css']
})
export class ResourceComponent implements OnInit {

  resource: Resource = new Resource('', '', '', false, '', {});

  constructor(private _rs: ResourceService, private route: ActivatedRoute) {
    route.params.subscribe(() => {
      const resourceName = route.snapshot.url[route.snapshot.url.length-1].path;
      this._rs.getResourceByName(resourceName).then(data => {
        this.resource = data;
      });
    })
  }

  ngOnInit(): void {
  }

}
