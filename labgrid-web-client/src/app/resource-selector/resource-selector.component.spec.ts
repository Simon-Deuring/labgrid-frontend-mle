import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResourceSelectorComponent } from './resource-selector.component';

describe('ResourceSelectorComponent', () => {
  let component: ResourceSelectorComponent;
  let fixture: ComponentFixture<ResourceSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ResourceSelectorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ResourceSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
