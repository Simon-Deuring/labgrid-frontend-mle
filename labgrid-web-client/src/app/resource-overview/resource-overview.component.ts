import { Component, OnInit } from '@angular/core';
import { Resource } from 'src/models/resource';
import { ResourceService } from '../services/resource.service';

@Component({
  selector: 'app-resource-overview',
  templateUrl: './resource-overview.component.html',
  styleUrls: ['./resource-overview.component.css']
})
export class ResourceOverviewComponent implements OnInit {

  resources: Resource[] = [];

  constructor(private _rs: ResourceService) {
    this._rs.getResources().then(data => {
      this.resources = data;
    });
  }

  ngOnInit(): void {
    
  }

}
