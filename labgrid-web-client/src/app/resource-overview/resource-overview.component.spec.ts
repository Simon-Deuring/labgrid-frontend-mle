import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResourceOverviewComponent } from './resource-overview.component';

describe('ResourceOverviewComponent', () => {
  let component: ResourceOverviewComponent;
  let fixture: ComponentFixture<ResourceOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ResourceOverviewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ResourceOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
